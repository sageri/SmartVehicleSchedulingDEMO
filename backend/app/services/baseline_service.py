"""
AI自動配車システムデモプロトタイプ - 基線計算サービス

最適化前の基準値（ベースライン）を計算します。
"""

import math
from typing import List, Dict, Any
from app.models.depot import Depot
from app.models.vehicle import Vehicle
from app.models.delivery import Delivery


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


class BaselineService:
    """
    基線計算サービス

    最適化を行わない単純な割当方法で基準値を算出します。
    """

    EARTH_RADIUS_KM = 6371.0  # 地球の半径（km）

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

        Reference:
            https://en.wikipedia.org/wiki/Haversine_formula
        """
        # 度をラジアンに変換
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine公式
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return self.EARTH_RADIUS_KM * c

    def calculate_simple_assignment(
        self, depots: List[Depot], vehicles: List[Vehicle], deliveries: List[Delivery]
    ) -> Dict[str, Any]:
        """
        単純割当法で基線メトリクスを計算

        アルゴリズム:
        1. 配送先を車両数で均等分割
        2. 各車両が拠点→配送先1→配送先2→...→拠点の順で巡回
        3. 総距離・総時間・総コストを計算

        Args:
            depots: 拠点リスト
            vehicles: 車両リスト
            deliveries: 配送先リスト

        Returns:
            Dict[str, Any]: 基線メトリクス
                - total_distance: 総距離（km）
                - total_duration: 総時間（分）
                - total_cost: 総コスト（¥）
                - average_utilization_weight: 平均重量積載率（%）
                - vehicle_count: 使用車両数（台）
                - method: "simple_assignment"
        """
        if not vehicles or not deliveries:
            return {
                "total_distance": 0.0,
                "total_duration": 0,
                "total_cost": 0.0,
                "average_utilization_weight": 0.0,
                "vehicle_count": 0,  # ✅ 新規追加フィールド
                "method": "simple_assignment",
            }

        # メイン拠点（最初の拠点を使用）
        main_depot = depots[0]

        # 配送先を車両数で分割
        deliveries_per_vehicle = len(deliveries) // len(vehicles)
        remainder = len(deliveries) % len(vehicles)

        total_distance = 0.0
        total_duration = 0
        total_cost = 0.0
        total_utilization_weight = 0.0
        used_vehicle_count = 0  # 実際に使用された車両数

        delivery_idx = 0

        for vehicle_idx, vehicle in enumerate(vehicles):
            # この車両が担当する配送先数
            num_deliveries = deliveries_per_vehicle + (1 if vehicle_idx < remainder else 0)

            if num_deliveries == 0:
                continue

            # 車両を使用
            used_vehicle_count += 1

            # 車両のルート: depot → delivery1 → delivery2 → ... → depot
            route_distance = 0.0
            route_duration = 0
            route_weight = 0.0

            # 現在位置（最初は拠点）
            current_lat = main_depot.latitude
            current_lon = main_depot.longitude

            # 配送先を順番に訪問
            for _ in range(num_deliveries):
                if delivery_idx >= len(deliveries):
                    break

                delivery = deliveries[delivery_idx]

                # 現在位置から配送先までの距離
                distance = self.calculate_haversine_distance(
                    current_lat, current_lon, delivery.latitude, delivery.longitude
                )
                route_distance += distance

                # 移動時間（仮定：平均速度30km/h）
                travel_time = int((distance / 30.0) * 60)  # 分
                route_duration += travel_time + delivery.service_time

                # 荷物重量を追加
                route_weight += delivery.weight

                # 次の配送先へ
                current_lat = delivery.latitude
                current_lon = delivery.longitude
                delivery_idx += 1

            # 最後の配送先から拠点へ戻る
            distance_back = self.calculate_haversine_distance(
                current_lat, current_lon, main_depot.latitude, main_depot.longitude
            )
            route_distance += distance_back
            route_duration += int((distance_back / 30.0) * 60)

            # コスト計算
            route_cost = (
                route_distance * vehicle.cost_per_km
                + (route_duration / 60.0) * vehicle.cost_per_hour
            )

            # 積載率計算
            utilization_weight = safe_divide(route_weight, vehicle.capacity_weight, 0.0) * 100.0

            # 累計
            total_distance += route_distance
            total_duration += route_duration
            total_cost += route_cost
            total_utilization_weight += utilization_weight

        # 平均積載率（使用された車両のみで計算）
        average_utilization_weight = (
            total_utilization_weight / used_vehicle_count if used_vehicle_count > 0 else 0.0
        )

        return {
            "total_distance": round(total_distance, 2),
            "total_duration": total_duration,
            "total_cost": round(total_cost, 2),
            "average_utilization_weight": round(average_utilization_weight, 2),
            "vehicle_count": used_vehicle_count,  # ✅ 新規追加フィールド
            "method": "simple_assignment",
        }
