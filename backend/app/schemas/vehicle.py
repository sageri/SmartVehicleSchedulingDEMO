"""
AI自動配車システムデモプロトタイプ - 車両Schemas
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Literal


class AvailableHours(BaseModel):
    """稼働可能時間"""

    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="稼働開始時刻 (HH:MM)")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="稼働終了時刻 (HH:MM)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"start_time": "08:00", "end_time": "18:00"}
        }
    )


class VehicleResponse(BaseModel):
    """
    車両レスポンス

    GET /api/v1/vehicles/{id} のレスポンス
    """

    id: str
    vehicle_type: Literal["2t", "4t"]
    capacity_weight: float = Field(..., description="最大積載重量 (kg)")
    capacity_volume: float = Field(..., description="最大積載容積 (m³)")
    depot_id: str
    available_hours: AvailableHours
    cost_per_km: float = Field(..., description="1kmあたりコスト (¥/km)")
    cost_per_hour: float = Field(..., description="1時間あたりコスト (¥/hour)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "vehicle-001",
                "vehicle_type": "2t",
                "capacity_weight": 2000.0,
                "capacity_volume": 8.0,
                "depot_id": "depot-tokyo",
                "available_hours": {"start_time": "08:00", "end_time": "18:00"},
                "cost_per_km": 50.0,
                "cost_per_hour": 2000.0,
            }
        },
    )

    @classmethod
    def from_orm_model(cls, vehicle):
        """
        ORM モデルから Pydantic モデルを作成

        Args:
            vehicle: Vehicle ORM モデル

        Returns:
            VehicleResponse: Pydantic レスポンスモデル
        """
        return cls(
            id=vehicle.id,
            vehicle_type=vehicle.vehicle_type,
            capacity_weight=vehicle.capacity_weight,
            capacity_volume=vehicle.capacity_volume,
            depot_id=vehicle.depot_id,
            available_hours=AvailableHours(
                start_time=vehicle.available_start_time.strftime("%H:%M"),
                end_time=vehicle.available_end_time.strftime("%H:%M"),
            ),
            cost_per_km=vehicle.cost_per_km,
            cost_per_hour=vehicle.cost_per_hour,
        )


class VehicleList(BaseModel):
    """
    車両リストレスポンス

    GET /api/v1/vehicles のレスポンス
    """

    vehicles: List[VehicleResponse]
    total: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicles": [
                    {
                        "id": "vehicle-001",
                        "vehicle_type": "2t",
                        "capacity_weight": 2000.0,
                        "capacity_volume": 8.0,
                        "depot_id": "depot-tokyo",
                        "available_hours": {"start_time": "08:00", "end_time": "18:00"},
                        "cost_per_km": 50.0,
                        "cost_per_hour": 2000.0,
                    }
                ],
                "total": 1,
            }
        }
    )
