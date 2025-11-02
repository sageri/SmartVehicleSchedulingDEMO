"""
AI自動配車システムデモプロトタイプ - 集荷拠点モデル
"""

from sqlalchemy import Column, String, Float, Time, DateTime
from datetime import datetime

from app.database import Base


class Depot(Base):
    """
    集荷拠点（Depot）モデル

    車両が出発・帰還する拠点を表します。

    Attributes:
        id: 拠点ID（主キー）
        name: 拠点名（例: "東京デポ"）
        latitude: 緯度（度）
        longitude: 経度（度）
        address: 住所
        operating_start_time: 営業開始時刻（HH:MM:SS）
        operating_end_time: 営業終了時刻（HH:MM:SS）
        created_at: 作成日時
        updated_at: 更新日時
    """

    __tablename__ = "depots"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    operating_start_time = Column(Time, nullable=False)
    operating_end_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Depot(id={self.id}, name={self.name})>"
