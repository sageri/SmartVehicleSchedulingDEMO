"""
AI自動配車システムデモプロトタイプ - Depots API

拠点情報を取得するエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import DepotRepository
from app.schemas.depot import DepotResponse, DepotList

router = APIRouter()


@router.get("", response_model=DepotList)
def get_depots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    拠点リストを取得

    Args:
        skip: スキップする件数（ページネーション用）
        limit: 最大取得件数

    Returns:
        DepotList: 拠点リスト
    """
    depot_repo = DepotRepository(db)
    depots = depot_repo.get_all(skip=skip, limit=limit)
    total = depot_repo.count()

    return DepotList(
        depots=[DepotResponse.from_orm_model(d) for d in depots], total=total
    )


@router.get("/{depot_id}", response_model=DepotResponse)
def get_depot(depot_id: str, db: Session = Depends(get_db)):
    """
    拠点を取得

    Args:
        depot_id: 拠点ID

    Returns:
        DepotResponse: 拠点情報

    Raises:
        HTTPException: 拠点が見つからない場合
    """
    depot_repo = DepotRepository(db)
    depot = depot_repo.get_by_id(depot_id)

    if not depot:
        raise HTTPException(status_code=404, detail=f"拠点ID {depot_id} が見つかりません")

    return DepotResponse.from_orm_model(depot)
