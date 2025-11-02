"""
AI自動配車システムデモプロトタイプ - Optimization API

VRP最適化を実行するエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import DepotRepository, VehicleRepository, DeliveryRepository
from app.schemas.optimization import OptimizationRequest, OptimizationResult
from app.services.vrp_service import VRPService

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResult, status_code=200)
def optimize_routes(
    request: OptimizationRequest, db: Session = Depends(get_db)
):
    """
    VRP最適化を実行

    指定された拠点、車両、配送先に対して、
    OR-Tools CVRPTWアルゴリズムで最適な配送ルートを生成します。

    Args:
        request: 最適化リクエスト
            - depot_ids: 対象拠点IDリスト
            - vehicle_ids: 使用車両IDリスト
            - delivery_ids: 配送先IDリスト

    Returns:
        OptimizationResult: 最適化結果
            - routes: 最適化されたルートリスト
            - total_distance: 総走行距離（km）
            - total_cost: 総コスト（¥）
            - baseline_metrics: 基線メトリクス
            - improvement_metrics: 改善指標

    Raises:
        HTTPException: データ検証エラーまたは最適化失敗時
    """
    depot_repo = DepotRepository(db)
    vehicle_repo = VehicleRepository(db)
    delivery_repo = DeliveryRepository(db)

    # 1. データ取得
    depots = depot_repo.get_by_ids(request.depot_ids)
    vehicles = vehicle_repo.get_by_ids(request.vehicle_ids)
    deliveries = delivery_repo.get_by_ids(request.delivery_ids)

    # 2. データ検証
    if not depots:
        raise HTTPException(
            status_code=400, detail="指定された拠点が見つかりません"
        )

    if not vehicles:
        raise HTTPException(
            status_code=400, detail="指定された車両が見つかりません"
        )

    if not deliveries:
        raise HTTPException(
            status_code=400, detail="指定された配送先が見つかりません"
        )

    # リクエストされたIDと実際に取得できたIDを比較
    found_depot_ids = {d.id for d in depots}
    missing_depot_ids = set(request.depot_ids) - found_depot_ids
    if missing_depot_ids:
        raise HTTPException(
            status_code=400,
            detail=f"拠点ID {', '.join(missing_depot_ids)} が見つかりません",
        )

    found_vehicle_ids = {v.id for v in vehicles}
    missing_vehicle_ids = set(request.vehicle_ids) - found_vehicle_ids
    if missing_vehicle_ids:
        raise HTTPException(
            status_code=400,
            detail=f"車両ID {', '.join(missing_vehicle_ids)} が見つかりません",
        )

    found_delivery_ids = {d.id for d in deliveries}
    missing_delivery_ids = set(request.delivery_ids) - found_delivery_ids
    if missing_delivery_ids:
        raise HTTPException(
            status_code=400,
            detail=f"配送先ID {', '.join(missing_delivery_ids)} が見つかりません",
        )

    # 3. VRP最適化実行
    try:
        vrp_service = VRPService()
        result = vrp_service.optimize(depots, vehicles, deliveries)
        return result

    except ValueError as e:
        # OR-Tools求解失敗
        raise HTTPException(
            status_code=422,
            detail=f"最適化に失敗しました: {str(e)}。制約が厳しすぎる可能性があります。",
        )

    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=500, detail=f"最適化中に予期しないエラーが発生しました: {str(e)}"
        )
