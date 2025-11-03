"""
AI自動配車システムデモプロトタイプ - 最適化Schemas
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import datetime


class OptimizationRequest(BaseModel):
    """
    VRP最適化リクエスト（同期API - 簡略版）

    POST /api/v1/optimization/optimize のリクエストボディ

    Story 002決定: 同期REST APIのため、最小限のパラメータのみ
    - アルゴリズム: OR-Tools CVRPTW固定
    - 最適化戦略: 距離最適化固定
    """

    depot_ids: List[str] = Field(..., min_length=1, description="対象拠点IDリスト")
    vehicle_ids: List[str] = Field(..., min_length=1, description="使用車両IDリスト")
    delivery_ids: List[str] = Field(..., min_length=1, description="配送先IDリスト")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "depot_ids": ["depot-tokyo"],
                "vehicle_ids": ["vehicle-001", "vehicle-002"],
                "delivery_ids": ["delivery-001", "delivery-002", "delivery-003"],
            }
        }
    )


class RouteStop(BaseModel):
    """
    ルート停車地点

    配送ルート内の1つの停車地点を表します。
    """

    delivery_id: str
    sequence: int = Field(..., ge=1, description="停車順序 (1から開始)")
    arrival_time: str = Field(..., description="到着時刻 (ISO 8601)")
    departure_time: str = Field(..., description="出発時刻 (ISO 8601)")
    distance_from_previous: float = Field(..., ge=0, description="前の地点からの距離 (km)")
    duration_from_previous: int = Field(..., ge=0, description="前の地点からの所要時間 (分)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "delivery_id": "delivery-001",
                "sequence": 1,
                "arrival_time": "2025-01-15T09:30:00Z",
                "departure_time": "2025-01-15T09:45:00Z",
                "distance_from_previous": 5.2,
                "duration_from_previous": 15,
            }
        }
    )


class Route(BaseModel):
    """
    配送ルート

    1台の車両の最適化された配送ルートを表します。
    """

    id: str
    vehicle_id: str
    depot_id: str
    stops: List[RouteStop] = Field(default_factory=list, description="停車地点リスト")
    total_distance: float = Field(..., ge=0, description="総走行距離 (km)")
    total_duration: int = Field(..., ge=0, description="総所要時間 (分)")
    total_weight: float = Field(..., ge=0, description="総積載重量 (kg)")
    total_volume: float = Field(..., ge=0, description="総積載容積 (m³)")
    total_cost: float = Field(..., ge=0, description="総コスト (¥)")
    utilization_weight: float = Field(..., ge=0, le=100, description="重量積載率 (%)")
    utilization_volume: float = Field(..., ge=0, le=100, description="容積積載率 (%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "route-001",
                "vehicle_id": "vehicle-001",
                "depot_id": "depot-tokyo",
                "stops": [
                    {
                        "delivery_id": "delivery-001",
                        "sequence": 1,
                        "arrival_time": "2025-01-15T09:30:00Z",
                        "departure_time": "2025-01-15T09:45:00Z",
                        "distance_from_previous": 5.2,
                        "duration_from_previous": 15,
                    }
                ],
                "total_distance": 45.8,
                "total_duration": 240,
                "total_weight": 850.0,
                "total_volume": 3.2,
                "total_cost": 7290.0,
                "utilization_weight": 42.5,
                "utilization_volume": 40.0,
            }
        }
    )


class BaselineMetrics(BaseModel):
    """
    基線メトリクス（最適化前の基準値）

    単純割当や貪欲法による最適化前の結果を表します。
    """

    total_distance: float = Field(..., ge=0, description="基線総距離 (km)")
    total_duration: int = Field(..., ge=0, description="基線総時間 (分)")
    total_cost: float = Field(..., ge=0, description="基線総コスト (¥)")
    average_utilization_weight: float = Field(..., ge=0, le=100, description="基線平均積載率 (%)")
    vehicle_count: int = Field(..., ge=0, description="基線使用車両数 (台)")  # ✅ 新規追加フィールド
    method: str = Field(default="simple_assignment", description="基線計算方法")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_distance": 250.5,
                "total_duration": 480,
                "total_cost": 35000.0,
                "average_utilization_weight": 65.3,
                "vehicle_count": 3,  # ✅ 新規追加フィールド
                "method": "simple_assignment",
            }
        }
    )


class ImprovementMetrics(BaseModel):
    """
    改善メトリクス（最適化による削減効果）

    最適化によって達成された改善を定量化します。
    """

    distance_reduction_km: float = Field(..., description="距離削減 (km)")
    distance_reduction_percent: float = Field(..., description="距離削減率 (%)")
    duration_reduction_minutes: int = Field(..., description="時間削減 (分)")
    cost_reduction_amount: float = Field(..., description="コスト削減金額 (¥)")
    cost_reduction_percent: float = Field(..., description="コスト削減率 (%)")
    utilization_improvement_percent: float = Field(..., description="積載率改善 (%)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "distance_reduction_km": 50.2,
                "distance_reduction_percent": 25.1,
                "duration_reduction_minutes": 90,
                "cost_reduction_amount": 8000.0,
                "cost_reduction_percent": 22.8,
                "utilization_improvement_percent": 12.5,
            }
        }
    )


class OptimizationResult(BaseModel):
    """
    VRP最適化結果

    POST /api/v1/optimization/optimize のレスポンス

    最適化計算の完全な結果を含みます。
    """

    id: str
    request_id: str
    routes: List[Route] = Field(default_factory=list, description="最適化されたルートリスト")
    total_distance: float = Field(..., ge=0, description="総走行距離 (km)")
    total_duration: int = Field(..., ge=0, description="総所要時間 (分)")
    total_cost: float = Field(..., ge=0, description="総コスト (¥)")
    average_utilization_weight: float = Field(..., ge=0, le=100, description="平均重量積載率 (%)")
    average_utilization_volume: float = Field(..., ge=0, le=100, description="平均容積積載率 (%)")
    computation_time: int = Field(..., ge=0, description="計算時間 (ms)")
    unassigned_deliveries: List[str] = Field(
        default_factory=list, description="未割当配送先IDリスト"
    )
    baseline_metrics: BaselineMetrics
    improvement_metrics: ImprovementMetrics
    created_at: str = Field(..., description="作成日時 (ISO 8601)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "result-001",
                "request_id": "req-001",
                "routes": [
                    {
                        "id": "route-001",
                        "vehicle_id": "vehicle-001",
                        "depot_id": "depot-tokyo",
                        "stops": [
                            {
                                "delivery_id": "delivery-001",
                                "sequence": 1,
                                "arrival_time": "2025-01-15T09:30:00Z",
                                "departure_time": "2025-01-15T09:45:00Z",
                                "distance_from_previous": 5.2,
                                "duration_from_previous": 15,
                            }
                        ],
                        "total_distance": 45.8,
                        "total_duration": 240,
                        "total_weight": 850.0,
                        "total_volume": 3.2,
                        "total_cost": 7290.0,
                        "utilization_weight": 42.5,
                        "utilization_volume": 40.0,
                    }
                ],
                "total_distance": 200.3,
                "total_duration": 390,
                "total_cost": 27000.0,
                "average_utilization_weight": 72.8,
                "average_utilization_volume": 68.5,
                "computation_time": 3450,
                "unassigned_deliveries": [],
                "baseline_metrics": {
                    "total_distance": 250.5,
                    "total_duration": 480,
                    "total_cost": 35000.0,
                    "average_utilization_weight": 65.3,
                    "vehicle_count": 3,  # ✅ 新規追加フィールド
                    "method": "simple_assignment",
                },
                "improvement_metrics": {
                    "distance_reduction_km": 50.2,
                    "distance_reduction_percent": 25.1,
                    "duration_reduction_minutes": 90,
                    "cost_reduction_amount": 8000.0,
                    "cost_reduction_percent": 22.8,
                    "utilization_improvement_percent": 12.5,
                },
                "created_at": "2025-01-15T08:00:00Z",
            }
        }
    )
