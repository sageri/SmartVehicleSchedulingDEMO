"""
AI自動配車システムデモプロトタイプ - 車両モデル
"""

from sqlalchemy import Column, String, Float, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Vehicle(Base):
    """
    車両（Vehicle）モデル

    配送に使用する車両を表します。

    Attributes:
        id: 車両ID（主キー）
        vehicle_type: 車両タイプ（"2t" または "4t"）
        capacity_weight: 最大積載重量（kg）
        capacity_volume: 最大積載容積（m³）
        depot_id: 所属拠点ID（外部キー）
        available_start_time: 稼働開始時刻（HH:MM:SS）
        available_end_time: 稼働終了時刻（HH:MM:SS）
        cost_per_km: 1kmあたりコスト（¥/km）
        cost_per_hour: 1時間あたりコスト（¥/hour）
        created_at: 作成日時
        updated_at: 更新日時

    Relationships:
        depot: 所属する拠点（Depot）
    """

    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)  # "2t" | "4t"
    capacity_weight = Column(Float, nullable=False)
    capacity_volume = Column(Float, nullable=False)
    depot_id = Column(String, ForeignKey("depots.id"), nullable=False, index=True)
    available_start_time = Column(Time, nullable=False)
    available_end_time = Column(Time, nullable=False)
    cost_per_km = Column(Float, nullable=False)
    cost_per_hour = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # リレーションシップ
    depot = relationship("Depot", backref="vehicles")

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, type={self.vehicle_type}, depot_id={self.depot_id})>"
