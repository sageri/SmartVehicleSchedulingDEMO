"""
AI自動配車システムデモプロトタイプ - FastAPI メインアプリケーション

このモジュールはFastAPIアプリケーションのエントリーポイントです。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# FastAPIアプリケーションインスタンス作成
app = FastAPI(
    title="AI自動配車システム API",
    description="車両ルート最適化（VRP）のための REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    ルートエンドポイント - APIの状態確認
    """
    return {
        "message": "AI自動配車システム API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "healthy"}


# 将来のAPI v1エンドポイントをここにインクルード
# from app.api.v1 import depots, vehicles, deliveries, optimization
# app.include_router(depots.router, prefix="/api/v1", tags=["depots"])
# app.include_router(vehicles.router, prefix="/api/v1", tags=["vehicles"])
# app.include_router(deliveries.router, prefix="/api/v1", tags=["deliveries"])
# app.include_router(optimization.router, prefix="/api/v1", tags=["optimization"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
