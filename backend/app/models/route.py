"""
AI自動配車システムデモプロトタイプ - ルートモデル
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Route(Base):
    """
    配送ルート（Route）モデル

    最適化された配送ルートを表します。

    Attributes:
        id: ルートID（主キー）
        vehicle_id: 使用車両ID（外部キー）
        depot_id: 出発拠点ID（外部キー）
        stops: 停車地点リスト（JSON配列） - RouteStop[]
        total_distance: 総走行距離（km）
        total_duration: 総所要時間（分）
        total_weight: 総積載重量（kg）
        total_volume: 総積載容積（m³）
        total_cost: 総コスト（¥）
        utilization_weight: 重量積載率（0-100%）
        utilization_volume: 容積積載率（0-100%）
        optimization_result_id: 所属する最適化結果ID（外部キー、nullable）
        created_at: 作成日時
        updated_at: 更新日時

    Relationships:
        vehicle: 使用する車両（Vehicle）
        depot: 出発する拠点（Depot）
        optimization_result: 所属する最適化結果（OptimizationResult）

    Note:
        stops フィールドは JSON 配列で、以下の構造を持ちます:
        [
            {
                "delivery_id": "delivery-1",
                "sequence": 1,
                "arrival_time": "2025-01-01T09:30:00Z",
                "departure_time": "2025-01-01T09:45:00Z",
                "distance_from_previous": 5.2,
                "duration_from_previous": 15
            },
            ...
        ]
    """

    __tablename__ = "routes"

    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False, index=True)
    depot_id = Column(String, ForeignKey("depots.id"), nullable=False, index=True)
    stops = Column(JSON, nullable=False, default=list)  # RouteStop[] as JSON
    total_distance = Column(Float, nullable=False)
    total_duration = Column(Integer, nullable=False)
    total_weight = Column(Float, nullable=False)
    total_volume = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    utilization_weight = Column(Float, nullable=False)
    utilization_volume = Column(Float, nullable=False)
    optimization_result_id = Column(
        String,
        ForeignKey("optimization_results.id"),
        nullable=True,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # リレーションシップ
    vehicle = relationship("Vehicle", backref="routes")
    depot = relationship("Depot", backref="routes")

    def __repr__(self) -> str:
        return f"<Route(id={self.id}, vehicle_id={self.vehicle_id}, stops={len(self.stops)})>"
