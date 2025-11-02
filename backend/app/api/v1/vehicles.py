"""
AI自動配車システムデモプロトタイプ - Vehicles API

車両情報を取得するエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Literal

from app.database import get_db
from app.repositories import VehicleRepository
from app.schemas.vehicle import VehicleResponse, VehicleList

router = APIRouter()


@router.get("", response_model=VehicleList)
def get_vehicles(
    depot_id: Optional[str] = Query(None, description="拠点IDでフィルタ"),
    vehicle_type: Optional[Literal["2t", "4t"]] = Query(None, description="車両タイプでフィルタ"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    車両リストを取得

    Args:
        depot_id: 拠点IDでフィルタ（オプション）
        vehicle_type: 車両タイプでフィルタ（オプション）
        skip: スキップする件数（ページネーション用）
        limit: 最大取得件数

    Returns:
        VehicleList: 車両リスト
    """
    vehicle_repo = VehicleRepository(db)

    # フィルタ適用
    if depot_id and vehicle_type:
        vehicles = vehicle_repo.get_by_depot_and_type(depot_id, vehicle_type)
        total = len(vehicles)
    elif depot_id:
        vehicles = vehicle_repo.get_by_depot(depot_id)
        total = vehicle_repo.count_by_depot(depot_id)
    elif vehicle_type:
        vehicles = vehicle_repo.get_by_type(vehicle_type)
        total = len(vehicles)
    else:
        vehicles = vehicle_repo.get_all(skip=skip, limit=limit)
        total = vehicle_repo.count()

    # ページネーション適用
    if depot_id or vehicle_type:
        vehicles = vehicles[skip : skip + limit]

    return VehicleList(
        vehicles=[VehicleResponse.from_orm_model(v) for v in vehicles], total=total
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """
    車両を取得

    Args:
        vehicle_id: 車両ID

    Returns:
        VehicleResponse: 車両情報

    Raises:
        HTTPException: 車両が見つからない場合
    """
    vehicle_repo = VehicleRepository(db)
    vehicle = vehicle_repo.get_by_id(vehicle_id)

    if not vehicle:
        raise HTTPException(status_code=404, detail=f"車両ID {vehicle_id} が見つかりません")

    return VehicleResponse.from_orm_model(vehicle)
