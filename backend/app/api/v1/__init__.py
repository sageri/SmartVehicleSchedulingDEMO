"""
AI自動配車システムデモプロトタイプ - API v1

REST APIエンドポイントを提供します。
"""

from fastapi import APIRouter
from app.api.v1 import depots, vehicles, deliveries, optimization, seed

# APIルーターを作成
api_router = APIRouter()

# 各エンドポイントを登録
api_router.include_router(seed.router, prefix="/seed", tags=["seed"])
api_router.include_router(depots.router, prefix="/depots", tags=["depots"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["deliveries"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["optimization"])

__all__ = ["api_router"]
