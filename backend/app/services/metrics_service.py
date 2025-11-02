"""
AI自動配車システムデモプロトタイプ - 改善指標計算サービス

最適化による改善効果を定量化します。
"""

from typing import Dict, Any, List
from app.schemas.optimization import Route


class MetricsService:
    """
    改善指標計算サービス

    基線メトリクスと最適化結果を比較し、改善効果を算出します。
    """

    def calculate_improvement_metrics(
        self, baseline: Dict[str, Any], optimized_routes: List[Route]
    ) -> Dict[str, Any]:
        """
        改善メトリクスを計算

        Args:
            baseline: 基線メトリクス
                - total_distance: 基線総距離（km）
                - total_duration: 基線総時間（分）
                - total_cost: 基線総コスト（¥）
                - average_utilization_weight: 基線平均積載率（%）
            optimized_routes: 最適化されたルートリスト

        Returns:
            Dict[str, Any]: 改善メトリクス
                - distance_reduction_km: 距離削減（km）
                - distance_reduction_percent: 距離削減率（%）
                - duration_reduction_minutes: 時間削減（分）
                - cost_reduction_amount: コスト削減金額（¥）
                - cost_reduction_percent: コスト削減率（%）
                - utilization_improvement_percent: 積載率改善（%）
        """
        # 最適化後の合計値を計算
        optimized_distance = sum(route.total_distance for route in optimized_routes)
        optimized_duration = sum(route.total_duration for route in optimized_routes)
        optimized_cost = sum(route.total_cost for route in optimized_routes)

        # ルート数が0の場合は平均0とする
        if optimized_routes:
            optimized_avg_utilization = sum(
                route.utilization_weight for route in optimized_routes
            ) / len(optimized_routes)
        else:
            optimized_avg_utilization = 0.0

        # 距離削減
        distance_reduction_km = baseline["total_distance"] - optimized_distance
        distance_reduction_percent = (
            (distance_reduction_km / baseline["total_distance"]) * 100.0
            if baseline["total_distance"] > 0
            else 0.0
        )

        # 時間削減
        duration_reduction_minutes = baseline["total_duration"] - optimized_duration

        # コスト削減
        cost_reduction_amount = baseline["total_cost"] - optimized_cost
        cost_reduction_percent = (
            (cost_reduction_amount / baseline["total_cost"]) * 100.0
            if baseline["total_cost"] > 0
            else 0.0
        )

        # 積載率改善
        utilization_improvement_percent = (
            optimized_avg_utilization - baseline["average_utilization_weight"]
        )

        return {
            "distance_reduction_km": round(distance_reduction_km, 2),
            "distance_reduction_percent": round(distance_reduction_percent, 2),
            "duration_reduction_minutes": duration_reduction_minutes,
            "cost_reduction_amount": round(cost_reduction_amount, 2),
            "cost_reduction_percent": round(cost_reduction_percent, 2),
            "utilization_improvement_percent": round(utilization_improvement_percent, 2),
        }

    def calculate_route_statistics(self, routes: List[Route]) -> Dict[str, Any]:
        """
        ルート統計情報を計算

        Args:
            routes: ルートリスト

        Returns:
            Dict[str, Any]: 統計情報
                - total_routes: ルート数
                - total_stops: 総停車数
                - avg_stops_per_route: ルートあたり平均停車数
                - avg_distance_per_route: ルートあたり平均距離（km）
                - avg_utilization_weight: 平均重量積載率（%）
                - avg_utilization_volume: 平均容積積載率（%）
        """
        if not routes:
            return {
                "total_routes": 0,
                "total_stops": 0,
                "avg_stops_per_route": 0.0,
                "avg_distance_per_route": 0.0,
                "avg_utilization_weight": 0.0,
                "avg_utilization_volume": 0.0,
            }

        total_stops = sum(len(route.stops) for route in routes)
        total_distance = sum(route.total_distance for route in routes)
        total_utilization_weight = sum(route.utilization_weight for route in routes)
        total_utilization_volume = sum(route.utilization_volume for route in routes)

        return {
            "total_routes": len(routes),
            "total_stops": total_stops,
            "avg_stops_per_route": round(total_stops / len(routes), 2),
            "avg_distance_per_route": round(total_distance / len(routes), 2),
            "avg_utilization_weight": round(total_utilization_weight / len(routes), 2),
            "avg_utilization_volume": round(total_utilization_volume / len(routes), 2),
        }
