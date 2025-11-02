"""
AI自動配車システムデモプロトタイプ - データモデル

SQLAlchemy ORM モデルをまとめてエクスポートします。
"""

from app.models.depot import Depot
from app.models.vehicle import Vehicle
from app.models.delivery import Delivery
from app.models.route import Route
from app.models.optimization_result import OptimizationResult

__all__ = [
    "Depot",
    "Vehicle",
    "Delivery",
    "Route",
    "OptimizationResult",
]
