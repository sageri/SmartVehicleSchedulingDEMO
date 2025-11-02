"""
AI自動配車システムデモプロトタイプ - Seed API

デモデータを生成するエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import time

from app.database import get_db
from app.models import Depot, Vehicle, Delivery
from app.repositories import DepotRepository, VehicleRepository, DeliveryRepository
from app.schemas.common import MessageResponse

router = APIRouter()


@router.post("/demo-data", response_model=MessageResponse, status_code=201)
def create_demo_data(db: Session = Depends(get_db)):
    """
    デモデータを生成

    既存のデータを全て削除し、新しいデモデータを作成します。

    Returns:
        MessageResponse: 生成結果メッセージ
    """
    depot_repo = DepotRepository(db)
    vehicle_repo = VehicleRepository(db)
    delivery_repo = DeliveryRepository(db)

    # 既存データを削除
    delivery_repo.delete_all()
    vehicle_repo.delete_all()
    depot_repo.delete_all()

    # 拠点作成（東京デポ）
    depot = Depot(
        id="depot-tokyo",
        name="東京デポ",
        latitude=35.6812,
        longitude=139.7671,
        address="東京都千代田区丸の内1-1-1",
        operating_start_time=time(8, 0),
        operating_end_time=time(18, 0),
    )
    depot_repo.create(depot)

    # 車両作成（3台）
    vehicles = [
        Vehicle(
            id="vehicle-001",
            vehicle_type="2t",
            capacity_weight=2000.0,
            capacity_volume=8.0,
            depot_id="depot-tokyo",
            available_start_time=time(8, 0),
            available_end_time=time(18, 0),
            cost_per_km=50.0,
            cost_per_hour=2000.0,
        ),
        Vehicle(
            id="vehicle-002",
            vehicle_type="2t",
            capacity_weight=2000.0,
            capacity_volume=8.0,
            depot_id="depot-tokyo",
            available_start_time=time(8, 0),
            available_end_time=time(18, 0),
            cost_per_km=50.0,
            cost_per_hour=2000.0,
        ),
        Vehicle(
            id="vehicle-003",
            vehicle_type="4t",
            capacity_weight=4000.0,
            capacity_volume=15.0,
            depot_id="depot-tokyo",
            available_start_time=time(8, 0),
            available_end_time=time(18, 0),
            cost_per_km=80.0,
            cost_per_hour=3000.0,
        ),
    ]
    for vehicle in vehicles:
        vehicle_repo.create(vehicle)

    # 配送先作成（20箇所）
    deliveries = [
        # 新宿エリア（午前指定）
        Delivery(
            id="delivery-001",
            customer_name="新宿商店A",
            latitude=35.6895,
            longitude=139.6917,
            address="東京都新宿区西新宿2-8-1",
            package_count=2,
            weight=150.0,
            volume=0.5,
            time_window="morning",
            service_time=15,
        ),
        Delivery(
            id="delivery-002",
            customer_name="新宿商店B",
            latitude=35.6950,
            longitude=139.6850,
            address="東京都新宿区新宿3-1-1",
            package_count=1,
            weight=100.0,
            volume=0.3,
            time_window="morning",
            service_time=10,
        ),
        Delivery(
            id="delivery-003",
            customer_name="新宿商店C",
            latitude=35.6910,
            longitude=139.6980,
            address="東京都新宿区西新宿1-1-3",
            package_count=2,
            weight=120.0,
            volume=0.4,
            time_window="morning",
            service_time=15,
        ),
        # 渋谷エリア（午後指定）
        Delivery(
            id="delivery-004",
            customer_name="渋谷商店A",
            latitude=35.6598,
            longitude=139.7023,
            address="東京都渋谷区道玄坂1-2-3",
            package_count=3,
            weight=200.0,
            volume=0.7,
            time_window="afternoon",
            service_time=20,
        ),
        Delivery(
            id="delivery-005",
            customer_name="渋谷商店B",
            latitude=35.6580,
            longitude=139.7016,
            address="東京都渋谷区渋谷2-24-12",
            package_count=2,
            weight=120.0,
            volume=0.4,
            time_window="afternoon",
            service_time=15,
        ),
        Delivery(
            id="delivery-006",
            customer_name="渋谷商店C",
            latitude=35.6620,
            longitude=139.7050,
            address="東京都渋谷区渋谷1-1-1",
            package_count=1,
            weight=80.0,
            volume=0.3,
            time_window="afternoon",
            service_time=10,
        ),
        # 品川エリア（時間指定なし）
        Delivery(
            id="delivery-007",
            customer_name="品川商店A",
            latitude=35.6284,
            longitude=139.7387,
            address="東京都港区港南2-16-1",
            package_count=1,
            weight=80.0,
            volume=0.2,
            time_window=None,
            service_time=10,
        ),
        Delivery(
            id="delivery-008",
            customer_name="品川商店B",
            latitude=35.6250,
            longitude=139.7420,
            address="東京都港区港南3-1-1",
            package_count=2,
            weight=140.0,
            volume=0.5,
            time_window=None,
            service_time=15,
        ),
        # 上野エリア（午前指定）
        Delivery(
            id="delivery-009",
            customer_name="上野商店A",
            latitude=35.7141,
            longitude=139.7774,
            address="東京都台東区上野7-1-1",
            package_count=2,
            weight=130.0,
            volume=0.4,
            time_window="morning",
            service_time=15,
        ),
        Delivery(
            id="delivery-010",
            customer_name="上野商店B",
            latitude=35.7100,
            longitude=139.7800,
            address="東京都台東区上野5-5-5",
            package_count=1,
            weight=90.0,
            volume=0.3,
            time_window="morning",
            service_time=10,
        ),
        # 池袋エリア（午後指定）
        Delivery(
            id="delivery-011",
            customer_name="池袋商店A",
            latitude=35.7295,
            longitude=139.7109,
            address="東京都豊島区南池袋1-28-1",
            package_count=2,
            weight=160.0,
            volume=0.6,
            time_window="afternoon",
            service_time=15,
        ),
        Delivery(
            id="delivery-012",
            customer_name="池袋商店B",
            latitude=35.7320,
            longitude=139.7150,
            address="東京都豊島区西池袋1-1-1",
            package_count=1,
            weight=100.0,
            volume=0.3,
            time_window="afternoon",
            service_time=10,
        ),
        # 六本木エリア（時間指定なし）
        Delivery(
            id="delivery-013",
            customer_name="六本木商店A",
            latitude=35.6627,
            longitude=139.7290,
            address="東京都港区六本木6-10-1",
            package_count=2,
            weight=150.0,
            volume=0.5,
            time_window=None,
            service_time=15,
        ),
        Delivery(
            id="delivery-014",
            customer_name="六本木商店B",
            latitude=35.6650,
            longitude=139.7310,
            address="東京都港区六本木3-1-1",
            package_count=1,
            weight=110.0,
            volume=0.4,
            time_window=None,
            service_time=10,
        ),
        # 秋葉原エリア（午前指定）
        Delivery(
            id="delivery-015",
            customer_name="秋葉原商店A",
            latitude=35.6982,
            longitude=139.7731,
            address="東京都千代田区外神田1-1-1",
            package_count=2,
            weight=140.0,
            volume=0.5,
            time_window="morning",
            service_time=15,
        ),
        Delivery(
            id="delivery-016",
            customer_name="秋葉原商店B",
            latitude=35.7000,
            longitude=139.7750,
            address="東京都千代田区外神田3-1-1",
            package_count=1,
            weight=95.0,
            volume=0.3,
            time_window="morning",
            service_time=10,
        ),
        # 目黒エリア（午後指定）
        Delivery(
            id="delivery-017",
            customer_name="目黒商店A",
            latitude=35.6339,
            longitude=139.7158,
            address="東京都品川区上大崎2-13-30",
            package_count=2,
            weight=170.0,
            volume=0.6,
            time_window="afternoon",
            service_time=15,
        ),
        Delivery(
            id="delivery-018",
            customer_name="目黒商店B",
            latitude=35.6360,
            longitude=139.7180,
            address="東京都品川区上大崎3-1-1",
            package_count=1,
            weight=105.0,
            volume=0.4,
            time_window="afternoon",
            service_time=10,
        ),
        # 浅草エリア（時間指定なし）
        Delivery(
            id="delivery-019",
            customer_name="浅草商店A",
            latitude=35.7148,
            longitude=139.7967,
            address="東京都台東区浅草2-3-1",
            package_count=2,
            weight=135.0,
            volume=0.5,
            time_window=None,
            service_time=15,
        ),
        Delivery(
            id="delivery-020",
            customer_name="浅草商店B",
            latitude=35.7120,
            longitude=139.7950,
            address="東京都台東区浅草1-1-1",
            package_count=1,
            weight=85.0,
            volume=0.3,
            time_window=None,
            service_time=10,
        ),
    ]
    for delivery in deliveries:
        delivery_repo.create(delivery)

    return MessageResponse(
        message="デモデータを作成しました",
        detail=f"拠点: 1件, 車両: {len(vehicles)}台, 配送先: {len(deliveries)}件",
    )
