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


def safe_divide(numerator: float, denominator: float, default_value: float = 0.0) -> float:
    """
    安全な除法：分母が0の場合のエラーを防ぐ

    Args:
        numerator: 分子
        denominator: 分母
        default_value: 分母が0の場合のデフォルト値

    Returns:
        float: 計算結果またはデフォルト値
    """
    if denominator == 0 or not (isinstance(denominator, (int, float)) and math.isfinite(denominator)):
        return default_value
    return numerator / denominator


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
        距離マトリクスを作成（Epic 005: Multi-Depot対応）

        Args:
            depots: 拠点リスト（全拠点）
            deliveries: 配送先リスト

        Returns:
            List[List[int]]: 距離マトリクス（m単位、整数）
                - インデックス0~N-1: 拠点（N=拠点数）
                - インデックスN~N+M-1: 配送先（M=配送先数）

        Epic 005例: 4拠点 + 100配送先 = 104ノード
                - インデックス0-3: 拠点（東京・横浜・川口・市川）
                - インデックス4-103: 配送先
        """
        # ロケーションリスト: [depot1, depot2, ..., delivery1, delivery2, ...]
        locations = [(d.latitude, d.longitude) for d in depots] + [
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
        OR-Tools用のデータモデルを作成（Epic 005: Multi-Depot対応）

        Args:
            depots: 拠点リスト（全拠点）
            vehicles: 車両リスト
            deliveries: 配送先リスト

        Returns:
            Dict[str, Any]: データモデル
                - starts: 各車両の出発拠点インデックスリスト
                - ends: 各車両の帰還拠点インデックスリスト
                - depot_to_index: 拠点ID → インデックス のマッピング
        """
        distance_matrix = self._create_distance_matrix(depots, deliveries)
        time_matrix = self._create_time_matrix(distance_matrix)

        # 拠点ID → インデックス のマッピング（Epic 005: Multi-Depot対応）
        depot_to_index = {depot.id: i for i, depot in enumerate(depots)}
        num_depots = len(depots)

        # 需要（重量）- 拠点はすべて0、配送先は実重量
        demands_weight = [0] * num_depots + [int(d.weight) for d in deliveries]

        # 需要（容積）- 拠点はすべて0、配送先は実容積（Story 5.2: 双重容量約束対応）
        demands_volume = [0] * num_depots + [int(d.volume * 100) for d in deliveries]  # m³ → リットル × 10

        # 車両容量（重量）
        vehicle_capacities_weight = [int(v.capacity_weight) for v in vehicles]

        # 車両容量（容積）- Story 5.2: 双重容量約束対応
        vehicle_capacities_volume = [int(v.capacity_volume * 100) for v in vehicles]  # m³ → リットル × 10

        # Epic 005: Multi-Depot対応 - 各車両の出発・帰還拠点を設定
        starts = [depot_to_index[v.depot_id] for v in vehicles]
        ends = [depot_to_index[v.depot_id] for v in vehicles]

        # 営業時間（全拠点が同じと仮定）
        depot_duration = (depots[0].operating_end_time.hour - depots[0].operating_start_time.hour) * 60

        # 時間窓（分単位）
        # 拠点の時間窓（全拠点に設定）
        time_windows = [(0, depot_duration)] * num_depots

        # 配送先の時間窓
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
            "demands_weight": demands_weight,                          # Story 5.2: 重量需要
            "demands_volume": demands_volume,                          # Story 5.2: 容積需要
            "vehicle_capacities_weight": vehicle_capacities_weight,    # Story 5.2: 重量容量
            "vehicle_capacities_volume": vehicle_capacities_volume,    # Story 5.2: 容積容量
            "num_vehicles": len(vehicles),
            "starts": starts,  # Multi-Depot: 各車両の出発拠点
            "ends": ends,      # Multi-Depot: 各車両の帰還拠点
            "time_windows": time_windows,
            "depot_to_index": depot_to_index,  # Multi-Depot: 拠点マッピング
            "num_depots": num_depots,          # Multi-Depot: 拠点数
            "depot_duration": depot_duration,
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

        # 5. 容量制約追加（Story 5.2: 双重容量約束対応）

        # 5.1 重量容量制約
        def demand_callback_weight(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return data["demands_weight"][from_node]

        demand_callback_weight_index = routing.RegisterUnaryTransitCallback(demand_callback_weight)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_weight_index,
            0,  # null capacity slack
            data["vehicle_capacities_weight"],
            True,  # start cumul to zero
            "CapacityWeight",
        )

        # 5.2 容積容量制約（Story 5.2: 新規追加）
        def demand_callback_volume(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return data["demands_volume"][from_node]

        demand_callback_volume_index = routing.RegisterUnaryTransitCallback(demand_callback_volume)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_volume_index,
            0,  # null capacity slack
            data["vehicle_capacities_volume"],
            True,  # start cumul to zero
            "CapacityVolume",
        )

        # 6. 時間制約追加
        def time_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = data["time_matrix"][from_node][to_node]
            # サービス時間を追加（配送先の場合）
            # Epic 005: Multi-Depot対応 - 拠点ノードをすべてスキップ
            if to_node >= data["num_depots"]:  # 配送先ノードのみ
                service_time = deliveries[to_node - data["num_depots"]].service_time
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

        # 9. ルート抽出（Epic 005: Multi-Depot対応）
        routes = self._extract_routes(
            solution, routing, manager, data, depots, vehicles, deliveries
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
        depots: List[Depot],  # Epic 005: Multi-Depot対応 - 全拠点を受け取る
        vehicles: List[Vehicle],
        deliveries: List[Delivery],
    ) -> List[Route]:
        """
        OR-Tools解からルート情報を抽出（Epic 005: Multi-Depot対応）

        Args:
            solution: OR-Tools解
            routing: ルーティングモデル
            manager: インデックスマネージャー
            data: データモデル
            depots: 拠点リスト（全拠点）
            vehicles: 車両リスト
            deliveries: 配送先リスト

        Returns:
            List[Route]: ルートリスト
        """
        routes = []
        time_dimension = routing.GetDimensionOrDie("Time")
        num_depots = data["num_depots"]

        for vehicle_idx in range(data["num_vehicles"]):
            index = routing.Start(vehicle_idx)
            route_stops = []
            route_distance = 0
            route_duration = 0
            route_weight = 0.0
            route_volume = 0.0

            # Epic 005: Multi-Depot対応 - 車両の所属拠点を取得
            vehicle = vehicles[vehicle_idx]
            vehicle_depot_idx = data["depot_to_index"][vehicle.depot_id]
            vehicle_depot = depots[vehicle_depot_idx]

            sequence = 1
            prev_node = vehicle_depot_idx  # Multi-Depot: 車両の出発拠点から開始

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)

                # Epic 005: Multi-Depot対応 - 拠点ノードをすべてスキップ
                if node >= num_depots:  # 配送先ノード（拠点以外）
                    delivery = deliveries[node - num_depots]

                    # 前のノードからの距離・時間
                    distance_from_prev = data["distance_matrix"][prev_node][node] / 1000.0  # km
                    duration_from_prev = data["time_matrix"][prev_node][node]  # 分

                    # 到着・出発時刻
                    time_var = time_dimension.CumulVar(index)
                    departure_minutes = solution.Min(time_var)
                    arrival_minutes = departure_minutes - delivery.service_time

                    # ISO 8601形式の時刻に変換
                    base_time = datetime.now(timezone.utc).replace(
                        hour=vehicle_depot.operating_start_time.hour,
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

            # 最後のノードから拠点への帰還（Epic 005: Multi-Depot対応）
            if prev_node != vehicle_depot_idx and prev_node >= num_depots:
                distance_back = data["distance_matrix"][prev_node][vehicle_depot_idx] / 1000.0
                duration_back = data["time_matrix"][prev_node][vehicle_depot_idx]
                route_distance += distance_back
                route_duration += duration_back

            # 停車がない場合はルートを追加しない
            if not route_stops:
                continue

            # コスト計算
            route_cost = route_distance * vehicle.cost_per_km + (
                route_duration / 60.0
            ) * vehicle.cost_per_hour

            # 積載率計算
            utilization_weight = safe_divide(route_weight, vehicle.capacity_weight, 0.0) * 100.0
            utilization_volume = safe_divide(route_volume, vehicle.capacity_volume, 0.0) * 100.0

            routes.append(
                Route(
                    id=f"route-{uuid.uuid4()}",
                    vehicle_id=vehicle.id,
                    depot_id=vehicle_depot.id,  # Epic 005: Multi-Depot対応 - 正しい拠点IDを設定
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
