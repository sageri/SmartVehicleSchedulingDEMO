"""
AI自動配車システムデモプロトタイプ - VRP最適化サービス

OR-Toolsを使用してCVRPTW（容量制約付き時間窓VRP）を解きます。
"""

import math
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Dict, Any, Optional

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from app.models.depot import Depot
from app.models.vehicle import Vehicle
from app.models.delivery import Delivery
from app.schemas.optimization import (
    OptimizationResult,
    Route,
    RouteStop,
    BaselineMetrics,
    ImprovementMetrics,
)
from app.services.baseline_service import BaselineService
from app.services.metrics_service import MetricsService
from app.config import settings


class VRPService:
    """
    VRP最適化サービス

    Google OR-ToolsのCVRPTWソルバーを使用して、
    車両ルーティング問題を最適化します。

    制約:
    - 容量制約（重量・容積）
    - 時間窓制約（morning/afternoon）
    - 各配送先は1度だけ訪問

    目標:
    - 総走行距離の最小化
    """

    EARTH_RADIUS_KM = 6371.0  # 地球の半径（km）
    AVERAGE_SPEED_KM_H = 30.0  # 平均速度（km/h）

    def __init__(self):
        self.baseline_service = BaselineService()
        self.metrics_service = MetricsService()

    def calculate_haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        2地点間のHaversine距離を計算

        Args:
            lat1: 地点1の緯度（度）
            lon1: 地点1の経度（度）
            lat2: 地点2の緯度（度）
            lon2: 地点2の経度（度）

        Returns:
            float: 距離（km）
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS_KM * c

    def _create_distance_matrix(
        self, depots: List[Depot], deliveries: List[Delivery]
    ) -> List[List[int]]:
        """
        距離マトリクスを作成

        Args:
            depots: 拠点リスト（最初の拠点のみ使用）
            deliveries: 配送先リスト

        Returns:
            List[List[int]]: 距離マトリクス（m単位、整数）
                - インデックス0: 拠点
                - インデックス1~N: 配送先
        """
        # ロケーションリスト: [depot, delivery1, delivery2, ...]
        locations = [(depots[0].latitude, depots[0].longitude)] + [
            (d.latitude, d.longitude) for d in deliveries
        ]

        num_locations = len(locations)
        distance_matrix = [[0] * num_locations for _ in range(num_locations)]

        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    distance_km = self.calculate_haversine_distance(
                        locations[i][0], locations[i][1], locations[j][0], locations[j][1]
                    )
                    # km → m に変換し、整数化
                    distance_matrix[i][j] = int(distance_km * 1000)

        return distance_matrix

    def _create_time_matrix(self, distance_matrix: List[List[int]]) -> List[List[int]]:
        """
        時間マトリクスを作成

        Args:
            distance_matrix: 距離マトリクス（m）

        Returns:
            List[List[int]]: 時間マトリクス（分）
        """
        num_locations = len(distance_matrix)
        time_matrix = [[0] * num_locations for _ in range(num_locations)]

        for i in range(num_locations):
            for j in range(num_locations):
                # 距離(m) → km → 時間(分)
                distance_km = distance_matrix[i][j] / 1000.0
                time_minutes = int((distance_km / self.AVERAGE_SPEED_KM_H) * 60)
                time_matrix[i][j] = time_minutes

        return time_matrix

    def _create_data_model(
        self, depots: List[Depot], vehicles: List[Vehicle], deliveries: List[Delivery]
    ) -> Dict[str, Any]:
        """
        OR-Tools用のデータモデルを作成

        Args:
            depots: 拠点リスト
            vehicles: 車両リスト
            deliveries: 配送先リスト

        Returns:
            Dict[str, Any]: データモデル
        """
        distance_matrix = self._create_distance_matrix(depots, deliveries)
        time_matrix = self._create_time_matrix(distance_matrix)

        # 需要（重量）- インデックス0は拠点なので0
        demands = [0] + [int(d.weight) for d in deliveries]

        # 車両容量
        vehicle_capacities = [int(v.capacity_weight) for v in vehicles]

        # デポインデックス（全車両が同じ拠点から出発）
        depot_index = 0
        starts = [depot_index] * len(vehicles)
        ends = [depot_index] * len(vehicles)

        # 時間窓（分単位）
        # OR-Toolsは0から累積するため、時間窓も0を基準とする
        # 営業時間: 8:00-18:00 → 0-600分（10時間）
        depot_duration = (depots[0].operating_end_time.hour - depots[0].operating_start_time.hour) * 60

        # Depot の時間窓（十分に広く設定）
        time_windows = [(0, depot_duration)]  # 0-600分

        for delivery in deliveries:
            if delivery.time_window == "morning":
                # 午前: 開始から4時間 (0-240分 = 8:00-12:00)
                time_windows.append((0, 240))
            elif delivery.time_window == "afternoon":
                # 午後: 5時間後から終了まで (300-600分 = 13:00-18:00)
                time_windows.append((300, depot_duration))
            else:
                # 時間指定なし: 営業時間内ならいつでも
                time_windows.append((0, depot_duration))

        return {
            "distance_matrix": distance_matrix,
            "time_matrix": time_matrix,
            "demands": demands,
            "vehicle_capacities": vehicle_capacities,
            "num_vehicles": len(vehicles),
            "starts": starts,
            "ends": ends,
            "time_windows": time_windows,
            "depot_index": depot_index,
            "depot_duration": depot_duration,  # 追加
        }

    def optimize(
        self, depots: List[Depot], vehicles: List[Vehicle], deliveries: List[Delivery]
    ) -> OptimizationResult:
        """
        VRP最適化を実行

        Args:
            depots: 拠点リスト
            vehicles: 車両リスト
            deliveries: 配送先リスト

        Returns:
            OptimizationResult: 最適化結果

        Raises:
            ValueError: 解が見つからない場合
        """
        import time as time_module

        start_time = time_module.time()

        # 1. データモデル作成
        data = self._create_data_model(depots, vehicles, deliveries)

        # 2. ルーティングインデックスマネージャー作成
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["starts"], data["ends"]
        )

        # 3. ルーティングモデル作成
        routing = pywrapcp.RoutingModel(manager)

        # 4. 距離コールバック登録
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 5. 容量制約追加
        def demand_callback(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],
            True,  # start cumul to zero
            "Capacity",
        )

        # 6. 時間制約追加
        def time_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = data["time_matrix"][from_node][to_node]
            # サービス時間を追加（配送先の場合）
            if to_node > 0:  # 拠点以外
                service_time = deliveries[to_node - 1].service_time
                return travel_time + service_time
            return travel_time

        time_callback_index = routing.RegisterTransitCallback(time_callback)

        routing.AddDimension(
            time_callback_index,
            30,  # 待機時間許容（分）
            data["depot_duration"],  # 最大ルート時間（分）= 営業時間
            True,  # start cumul to zero（重要！）
            "Time",
        )

        time_dimension = routing.GetDimensionOrDie("Time")

        # 時間窓を設定（全ノードに設定）
        for location_idx, time_window in enumerate(data["time_windows"]):
            index = manager.NodeToIndex(location_idx)
            # 有効なインデックスのみ処理
            if index >= 0:
                time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # 7. 探索パラメータ設定
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = settings.VRP_TIME_LIMIT_SECONDS

        # 8. 求解実行
        solution = routing.SolveWithParameters(search_parameters)

        computation_time = int((time_module.time() - start_time) * 1000)  # ms

        if not solution:
            raise ValueError("VRP求解に失敗しました。実行可能解が見つかりません。")

        # 9. ルート抽出
        routes = self._extract_routes(
            solution, routing, manager, data, depots[0], vehicles, deliveries
        )

        # 10. 基線メトリクス計算
        baseline = self.baseline_service.calculate_simple_assignment(
            depots, vehicles, deliveries
        )

        # 11. 改善メトリクス計算
        improvement = self.metrics_service.calculate_improvement_metrics(baseline, routes)

        # 12. 未割当配送先の抽出
        assigned_delivery_ids = set()
        for route in routes:
            for stop in route.stops:
                assigned_delivery_ids.add(stop.delivery_id)

        all_delivery_ids = {d.id for d in deliveries}
        unassigned_deliveries = list(all_delivery_ids - assigned_delivery_ids)

        # 13. 結果作成
        result = OptimizationResult(
            id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            routes=routes,
            total_distance=sum(r.total_distance for r in routes),
            total_duration=sum(r.total_duration for r in routes),
            total_cost=sum(r.total_cost for r in routes),
            average_utilization_weight=(
                sum(r.utilization_weight for r in routes) / len(routes)
                if routes
                else 0.0
            ),
            average_utilization_volume=(
                sum(r.utilization_volume for r in routes) / len(routes) if routes else 0.0
            ),
            computation_time=computation_time,
            unassigned_deliveries=unassigned_deliveries,
            baseline_metrics=BaselineMetrics(**baseline),
            improvement_metrics=ImprovementMetrics(**improvement),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        return result

    def _extract_routes(
        self,
        solution,
        routing,
        manager,
        data: Dict[str, Any],
        depot: Depot,
        vehicles: List[Vehicle],
        deliveries: List[Delivery],
    ) -> List[Route]:
        """
        OR-Tools解からルート情報を抽出

        Args:
            solution: OR-Tools解
            routing: ルーティングモデル
            manager: インデックスマネージャー
            data: データモデル
            depot: 拠点
            vehicles: 車両リスト
            deliveries: 配送先リスト

        Returns:
            List[Route]: ルートリスト
        """
        routes = []
        time_dimension = routing.GetDimensionOrDie("Time")

        for vehicle_idx in range(data["num_vehicles"]):
            index = routing.Start(vehicle_idx)
            route_stops = []
            route_distance = 0
            route_duration = 0
            route_weight = 0.0
            route_volume = 0.0

            sequence = 1
            prev_node = data["depot_index"]

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)

                if node != data["depot_index"]:  # 拠点以外
                    delivery = deliveries[node - 1]

                    # 前のノードからの距離・時間
                    distance_from_prev = data["distance_matrix"][prev_node][node] / 1000.0  # km
                    duration_from_prev = data["time_matrix"][prev_node][node]  # 分

                    # 到着・出発時刻
                    time_var = time_dimension.CumulVar(index)
                    arrival_minutes = solution.Min(time_var)
                    departure_minutes = solution.Min(time_var) + delivery.service_time

                    # ISO 8601形式の時刻に変換（簡易実装）
                    base_time = datetime.now(timezone.utc).replace(
                        hour=depot.operating_start_time.hour,
                        minute=0,
                        second=0,
                        microsecond=0,
                    )
                    arrival_time = (base_time + timedelta(minutes=arrival_minutes)).isoformat()
                    departure_time = (
                        base_time + timedelta(minutes=departure_minutes)
                    ).isoformat()

                    route_stops.append(
                        RouteStop(
                            delivery_id=delivery.id,
                            sequence=sequence,
                            arrival_time=arrival_time,
                            departure_time=departure_time,
                            distance_from_previous=round(distance_from_prev, 2),
                            duration_from_previous=duration_from_prev,
                        )
                    )

                    route_distance += distance_from_prev
                    route_duration += duration_from_prev + delivery.service_time
                    route_weight += delivery.weight
                    route_volume += delivery.volume
                    sequence += 1

                prev_node = node
                index = solution.Value(routing.NextVar(index))

            # 最後のノードから拠点への帰還
            if prev_node != data["depot_index"]:
                distance_back = data["distance_matrix"][prev_node][data["depot_index"]] / 1000.0
                duration_back = data["time_matrix"][prev_node][data["depot_index"]]
                route_distance += distance_back
                route_duration += duration_back

            # 停車がない場合はルートを追加しない
            if not route_stops:
                continue

            vehicle = vehicles[vehicle_idx]

            # コスト計算
            route_cost = route_distance * vehicle.cost_per_km + (
                route_duration / 60.0
            ) * vehicle.cost_per_hour

            # 積載率計算
            utilization_weight = (route_weight / vehicle.capacity_weight) * 100.0
            utilization_volume = (route_volume / vehicle.capacity_volume) * 100.0

            routes.append(
                Route(
                    id=f"route-{uuid.uuid4()}",
                    vehicle_id=vehicle.id,
                    depot_id=depot.id,
                    stops=route_stops,
                    total_distance=round(route_distance, 2),
                    total_duration=route_duration,
                    total_weight=round(route_weight, 2),
                    total_volume=round(route_volume, 2),
                    total_cost=round(route_cost, 2),
                    utilization_weight=round(utilization_weight, 2),
                    utilization_volume=round(utilization_volume, 2),
                )
            )

        return routes
