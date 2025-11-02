"""
AI自動配車システムデモプロトタイプ - 配送先Schemas
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal, Optional


class DeliveryResponse(BaseModel):
    """
    配送先レスポンス

    GET /api/v1/deliveries/{id} のレスポンス
    """

    id: str
    customer_name: str
    latitude: float
    longitude: float
    address: str
    package_count: int = Field(..., ge=1, le=3, description="荷物個数 (1-3)")
    weight: float = Field(..., gt=0, description="荷物重量 (kg)")
    volume: float = Field(..., gt=0, description="荷物容積 (m³)")
    time_window: Optional[Literal["morning", "afternoon"]] = Field(
        None, description="時間窓 (morning | afternoon | null)"
    )
    service_time: int = Field(..., gt=0, description="サービス時間 (分)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "delivery-001",
                "customer_name": "山田商店",
                "latitude": 35.6895,
                "longitude": 139.6917,
                "address": "東京都新宿区西新宿2-8-1",
                "package_count": 2,
                "weight": 150.0,
                "volume": 0.5,
                "time_window": "morning",
                "service_time": 15,
            }
        },
    )


class DeliveryList(BaseModel):
    """
    配送先リストレスポンス

    GET /api/v1/deliveries のレスポンス
    """

    deliveries: List[DeliveryResponse]
    total: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "deliveries": [
                    {
                        "id": "delivery-001",
                        "customer_name": "山田商店",
                        "latitude": 35.6895,
                        "longitude": 139.6917,
                        "address": "東京都新宿区西新宿2-8-1",
                        "package_count": 2,
                        "weight": 150.0,
                        "volume": 0.5,
                        "time_window": "morning",
                        "service_time": 15,
                    }
                ],
                "total": 1,
            }
        }
    )
