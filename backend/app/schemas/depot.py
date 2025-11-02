"""
AI自動配車システムデモプロトタイプ - 拠点Schemas
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import time


class OperatingHours(BaseModel):
    """営業時間"""

    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="営業開始時刻 (HH:MM)")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="営業終了時刻 (HH:MM)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"start_time": "08:00", "end_time": "18:00"}
        }
    )


class DepotResponse(BaseModel):
    """
    拠点レスポンス

    GET /api/v1/depots/{id} のレスポンス
    """

    id: str
    name: str
    latitude: float
    longitude: float
    address: str
    operating_hours: OperatingHours

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "depot-tokyo",
                "name": "東京デポ",
                "latitude": 35.6812,
                "longitude": 139.7671,
                "address": "東京都千代田区丸の内1-1-1",
                "operating_hours": {"start_time": "08:00", "end_time": "18:00"},
            }
        },
    )

    @classmethod
    def from_orm_model(cls, depot):
        """
        ORM モデルから Pydantic モデルを作成

        Args:
            depot: Depot ORM モデル

        Returns:
            DepotResponse: Pydantic レスポンスモデル
        """
        return cls(
            id=depot.id,
            name=depot.name,
            latitude=depot.latitude,
            longitude=depot.longitude,
            address=depot.address,
            operating_hours=OperatingHours(
                start_time=depot.operating_start_time.strftime("%H:%M"),
                end_time=depot.operating_end_time.strftime("%H:%M"),
            ),
        )


class DepotList(BaseModel):
    """
    拠点リストレスポンス

    GET /api/v1/depots のレスポンス
    """

    depots: List[DepotResponse]
    total: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "depots": [
                    {
                        "id": "depot-tokyo",
                        "name": "東京デポ",
                        "latitude": 35.6812,
                        "longitude": 139.7671,
                        "address": "東京都千代田区丸の内1-1-1",
                        "operating_hours": {"start_time": "08:00", "end_time": "18:00"},
                    }
                ],
                "total": 1,
            }
        }
    )
