"""
AI自動配車システムデモプロトタイプ - 最適化結果モデル
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class OptimizationResult(Base):
    """
    最適化結果（OptimizationResult）モデル

    VRP最適化計算の結果を表します。

    Attributes:
        id: 結果ID（主キー）
        request_id: リクエストID（トレース用）
        total_distance: 総走行距離（km）
        total_duration: 総所要時間（分）
        total_cost: 総コスト（¥）
        average_utilization_weight: 平均重量積載率（%）
        average_utilization_volume: 平均容積積載率（%）
        computation_time: 計算時間（ms）
        unassigned_deliveries: 未割当配送先IDリスト（JSON配列）
        baseline_metrics: 基線メトリクス（JSON） - BaselineMetrics
        improvement_metrics: 改善メトリクス（JSON） - ImprovementMetrics
        created_at: 作成日時
        updated_at: 更新日時

    Relationships:
        routes: 生成されたルートリスト（Route[]）

    Note:
        baseline_metrics の構造:
        {
            "total_distance": 250.5,
            "total_duration": 480,
            "total_cost": 35000,
            "average_utilization_weight": 65.3,
            "method": "simple_assignment"
        }

        improvement_metrics の構造:
        {
            "distance_reduction_km": 50.2,
            "distance_reduction_percent": 25.1,
            "duration_reduction_minutes": 90,
            "cost_reduction_amount": 8000,
            "cost_reduction_percent": 22.8,
            "utilization_improvement_percent": 12.5
        }
    """

    __tablename__ = "optimization_results"

    id = Column(String, primary_key=True, index=True)
    request_id = Column(String, nullable=False, index=True)
    total_distance = Column(Float, nullable=False)
    total_duration = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)
    average_utilization_weight = Column(Float, nullable=False)
    average_utilization_volume = Column(Float, nullable=False)
    computation_time = Column(Integer, nullable=False)
    unassigned_deliveries = Column(JSON, nullable=False, default=list)  # string[] as JSON
    baseline_metrics = Column(JSON, nullable=False)  # BaselineMetrics as JSON
    improvement_metrics = Column(JSON, nullable=False)  # ImprovementMetrics as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # リレーションシップ
    routes = relationship("Route", backref="optimization_result", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<OptimizationResult(id={self.id}, routes={len(self.routes)}, distance={self.total_distance}km)>"
