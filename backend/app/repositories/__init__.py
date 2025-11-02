"""
AI自動配車システムデモプロトタイプ - Repository層

データアクセスを抽象化し、ビジネスロジックとDBを分離します。
"""

from app.repositories.base import BaseRepository
from app.repositories.depot_repository import DepotRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.delivery_repository import DeliveryRepository

__all__ = [
    "BaseRepository",
    "DepotRepository",
    "VehicleRepository",
    "DeliveryRepository",
]
