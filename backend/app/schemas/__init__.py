"""
AI自動配車システムデモプロトタイプ - API Schemas

Pydantic schemas for request/response validation.
"""

from app.schemas.depot import DepotResponse, DepotList
from app.schemas.vehicle import VehicleResponse, VehicleList
from app.schemas.delivery import DeliveryResponse, DeliveryList
from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResult,
    Route,
    RouteStop,
    BaselineMetrics,
    ImprovementMetrics,
)
from app.schemas.common import MessageResponse, ErrorDetail

__all__ = [
    # Depot
    "DepotResponse",
    "DepotList",
    # Vehicle
    "VehicleResponse",
    "VehicleList",
    # Delivery
    "DeliveryResponse",
    "DeliveryList",
    # Optimization
    "OptimizationRequest",
    "OptimizationResult",
    "Route",
    "RouteStop",
    "BaselineMetrics",
    "ImprovementMetrics",
    # Common
    "MessageResponse",
    "ErrorDetail",
]
