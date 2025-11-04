"""
AI自動配車システムデモプロトタイプ - 配送先モデル
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class Delivery(Base):
    """
    配送先（Delivery）モデル

    配送が必要な顧客・荷物を表します。

    Attributes:
        id: 配送ID（主キー）
        customer_name: 顧客名
        latitude: 緯度（度）
        longitude: 経度（度）
        address: 住所
        package_count: 荷物個数（1-3）
        weight: 荷物重量（kg）
        volume: 荷物容積（m³）
        time_window: 時間窓（"morning" | "afternoon" | null）
        service_time: サービス時間（分） - 配送に必要な時間
        depot_id: 所属拠点ID（Epic 005: Multi-Depot対応 - 配送先と拠点の関連付け）
        created_at: 作成日時
        updated_at: 更新日時
    """

    __tablename__ = "deliveries"

    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    package_count = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    time_window = Column(String, nullable=True)  # "morning" | "afternoon" | null
    service_time = Column(Integer, nullable=False)
    depot_id = Column(String, ForeignKey("depots.id"), nullable=False, index=True)  # Epic 005: Multi-Depot対応
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Delivery(id={self.id}, customer={self.customer_name}, depot={self.depot_id}, weight={self.weight}kg)>"
