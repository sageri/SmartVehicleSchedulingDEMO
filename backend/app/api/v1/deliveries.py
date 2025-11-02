"""
AI自動配車システムデモプロトタイプ - Deliveries API

配送先情報を取得するエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal

from app.database import get_db
from app.repositories import DeliveryRepository
from app.schemas.delivery import DeliveryResponse, DeliveryList

router = APIRouter()


@router.get("", response_model=DeliveryList)
def get_deliveries(
    time_window: Optional[Literal["morning", "afternoon"]] = Query(
        None, description="時間窓でフィルタ"
    ),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    配送先リストを取得

    Args:
        time_window: 時間窓でフィルタ（オプション）
        skip: スキップする件数（ページネーション用）
        limit: 最大取得件数

    Returns:
        DeliveryList: 配送先リスト
    """
    delivery_repo = DeliveryRepository(db)

    # フィルタ適用
    if time_window:
        deliveries = delivery_repo.get_by_time_window(time_window)
        total = delivery_repo.count_by_time_window(time_window)
        # ページネーション適用
        deliveries = deliveries[skip : skip + limit]
    else:
        deliveries = delivery_repo.get_all(skip=skip, limit=limit)
        total = delivery_repo.count()

    return DeliveryList(deliveries=deliveries, total=total)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: str, db: Session = Depends(get_db)):
    """
    配送先を取得

    Args:
        delivery_id: 配送先ID

    Returns:
        DeliveryResponse: 配送先情報

    Raises:
        HTTPException: 配送先が見つからない場合
    """
    delivery_repo = DeliveryRepository(db)
    delivery = delivery_repo.get_by_id(delivery_id)

    if not delivery:
        raise HTTPException(
            status_code=404, detail=f"配送先ID {delivery_id} が見つかりません"
        )

    return delivery
