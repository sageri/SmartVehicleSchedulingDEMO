"""
Repository層テストスクリプト

基本的なCRUD操作をテストします。
"""

import sys
from pathlib import Path
from datetime import time, datetime

# プロジェクトルートを sys.path に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import SessionLocal, init_db
from app.repositories import DepotRepository, VehicleRepository, DeliveryRepository
from app.models import Depot, Vehicle, Delivery


def test_repositories():
    """Repository層のテスト"""

    print("🚀 Repository層テストを開始します...\n")

    # データベース初期化
    init_db()

    # セッション作成
    db = SessionLocal()

    try:
        # ======================
        # Depot Repository テスト
        # ======================
        print("=" * 60)
        print("📍 Depot Repository テスト")
        print("=" * 60)

        depot_repo = DepotRepository(db)

        # Create
        test_depot = Depot(
            id="depot-test-001",
            name="テストデポ",
            latitude=35.6812,
            longitude=139.7671,
            address="東京都千代田区丸の内1-1-1",
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )
        created_depot = depot_repo.create(test_depot)
        print(f"✅ Create: {created_depot.name} (ID: {created_depot.id})")

        # Read
        fetched_depot = depot_repo.get_by_id("depot-test-001")
        print(f"✅ Read by ID: {fetched_depot.name if fetched_depot else 'Not Found'}")

        # Count
        count = depot_repo.count()
        print(f"✅ Count: {count} depots")

        # Get All
        all_depots = depot_repo.get_all()
        print(f"✅ Get All: {len(all_depots)} depots")

        # ======================
        # Vehicle Repository テスト
        # ======================
        print("\n" + "=" * 60)
        print("🚚 Vehicle Repository テスト")
        print("=" * 60)

        vehicle_repo = VehicleRepository(db)

        # Create
        test_vehicle = Vehicle(
            id="vehicle-test-001",
            vehicle_type="2t",
            capacity_weight=2000.0,
            capacity_volume=8.0,
            depot_id="depot-test-001",
            available_start_time=time(8, 0),
            available_end_time=time(18, 0),
            cost_per_km=50.0,
            cost_per_hour=2000.0,
        )
        created_vehicle = vehicle_repo.create(test_vehicle)
        print(f"✅ Create: {created_vehicle.vehicle_type} (ID: {created_vehicle.id})")

        # Get by depot
        depot_vehicles = vehicle_repo.get_by_depot("depot-test-001")
        print(f"✅ Get by Depot: {len(depot_vehicles)} vehicles")

        # Get by type
        type_vehicles = vehicle_repo.get_by_type("2t")
        print(f"✅ Get by Type (2t): {len(type_vehicles)} vehicles")

        # Count by depot
        depot_count = vehicle_repo.count_by_depot("depot-test-001")
        print(f"✅ Count by Depot: {depot_count} vehicles")

        # ======================
        # Delivery Repository テスト
        # ======================
        print("\n" + "=" * 60)
        print("📦 Delivery Repository テスト")
        print("=" * 60)

        delivery_repo = DeliveryRepository(db)

        # Create - Morning delivery
        test_delivery_1 = Delivery(
            id="delivery-test-001",
            customer_name="山田商店",
            latitude=35.6895,
            longitude=139.6917,
            address="東京都新宿区西新宿2-8-1",
            package_count=2,
            weight=150.0,
            volume=0.5,
            time_window="morning",
            service_time=15,
        )
        created_delivery_1 = delivery_repo.create(test_delivery_1)
        print(f"✅ Create (Morning): {created_delivery_1.customer_name}")

        # Create - Afternoon delivery
        test_delivery_2 = Delivery(
            id="delivery-test-002",
            customer_name="佐藤商店",
            latitude=35.6950,
            longitude=139.6850,
            address="東京都新宿区新宿3-1-1",
            package_count=1,
            weight=80.0,
            volume=0.3,
            time_window="afternoon",
            service_time=10,
        )
        created_delivery_2 = delivery_repo.create(test_delivery_2)
        print(f"✅ Create (Afternoon): {created_delivery_2.customer_name}")

        # Get by time window
        morning_deliveries = delivery_repo.get_by_time_window("morning")
        print(f"✅ Get by Time Window (morning): {len(morning_deliveries)} deliveries")

        afternoon_deliveries = delivery_repo.get_by_time_window("afternoon")
        print(f"✅ Get by Time Window (afternoon): {len(afternoon_deliveries)} deliveries")

        # Search by customer name
        search_results = delivery_repo.search_by_customer_name("山田")
        print(f"✅ Search by Customer Name ('山田'): {len(search_results)} results")

        # Get statistics
        stats = delivery_repo.get_statistics()
        print(f"✅ Statistics:")
        print(f"   - Total: {stats['total']}")
        print(f"   - Morning: {stats['morning']}")
        print(f"   - Afternoon: {stats['afternoon']}")
        print(f"   - Average Weight: {stats['avg_weight']:.2f} kg")
        print(f"   - Total Weight: {stats['total_weight']:.2f} kg")

        # ======================
        # Cleanup テスト
        # ======================
        print("\n" + "=" * 60)
        print("🧹 Cleanup テスト")
        print("=" * 60)

        # Delete
        deleted = delivery_repo.delete("delivery-test-001")
        print(f"✅ Delete delivery-test-001: {deleted}")

        deleted = vehicle_repo.delete("vehicle-test-001")
        print(f"✅ Delete vehicle-test-001: {deleted}")

        deleted = depot_repo.delete("depot-test-001")
        print(f"✅ Delete depot-test-001: {deleted}")

        # Verify deletion
        exists = depot_repo.exists("depot-test-001")
        print(f"✅ Verify deletion (should be False): {exists}")

        print("\n" + "=" * 60)
        print("✅ すべてのテストが成功しました！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    test_repositories()
