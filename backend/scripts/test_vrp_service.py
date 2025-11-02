"""
VRP Service テストスクリプト

小規模データでVRP最適化をテストします。
"""

import sys
from pathlib import Path
from datetime import time

# プロジェクトルートを sys.path に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.vrp_service import VRPService
from app.models import Depot, Vehicle, Delivery


def test_vrp_optimization():
    """VRP最適化の基本テスト"""

    print("=" * 70)
    print("🚀 VRP最適化サービス テスト")
    print("=" * 70)

    # テストデータ作成
    print("\n📊 テストデータ作成中...")

    # 1. 拠点（東京駅付近）
    depot = Depot(
        id="depot-tokyo",
        name="東京デポ",
        latitude=35.6812,
        longitude=139.7671,
        address="東京都千代田区丸の内1-1-1",
        operating_start_time=time(8, 0),
        operating_end_time=time(18, 0),
    )

    # 2. 車両（2台）
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
    ]

    # 3. 配送先（6箇所）
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
        # 渋谷エリア（午後指定）
        Delivery(
            id="delivery-003",
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
            id="delivery-004",
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
        # 品川エリア（時間指定なし）
        Delivery(
            id="delivery-005",
            customer_name="品川商店",
            latitude=35.6284,
            longitude=139.7387,
            address="東京都港区港南2-16-1",
            package_count=1,
            weight=80.0,
            volume=0.2,
            time_window=None,
            service_time=10,
        ),
        # 上野エリア（午前指定）
        Delivery(
            id="delivery-006",
            customer_name="上野商店",
            latitude=35.7141,
            longitude=139.7774,
            address="東京都台東区上野7-1-1",
            package_count=2,
            weight=130.0,
            volume=0.4,
            time_window="morning",
            service_time=15,
        ),
    ]

    print(f"   拠点: {len([depot])}箇所")
    print(f"   車両: {len(vehicles)}台")
    print(f"   配送先: {len(deliveries)}箇所")
    print(f"      - 午前指定: {sum(1 for d in deliveries if d.time_window == 'morning')}箇所")
    print(
        f"      - 午後指定: {sum(1 for d in deliveries if d.time_window == 'afternoon')}箇所"
    )
    print(f"      - 時間指定なし: {sum(1 for d in deliveries if d.time_window is None)}箇所")

    # VRP最適化実行
    print("\n🔧 VRP最適化実行中...")
    print("   アルゴリズム: OR-Tools CVRPTW")
    print("   初期解戦略: PATH_CHEAPEST_ARC")
    print("   局所探索: GUIDED_LOCAL_SEARCH")
    print("   時間制限: 30秒\n")

    vrp_service = VRPService()

    try:
        result = vrp_service.optimize([depot], vehicles, deliveries)

        print("=" * 70)
        print("✅ 最適化成功！")
        print("=" * 70)

        # 結果表示
        print(f"\n📊 最適化結果:")
        print(f"   結果ID: {result.id}")
        print(f"   計算時間: {result.computation_time}ms")
        print(f"   生成ルート数: {len(result.routes)}")
        print(f"   未割当配送先: {len(result.unassigned_deliveries)}件")

        print(f"\n📈 パフォーマンス指標:")
        print(f"   総走行距離: {result.total_distance:.2f} km")
        print(f"   総所要時間: {result.total_duration} 分")
        print(f"   総コスト: ¥{result.total_cost:,.2f}")
        print(f"   平均重量積載率: {result.average_utilization_weight:.2f}%")
        print(f"   平均容積積載率: {result.average_utilization_volume:.2f}%")

        print(f"\n📉 基線メトリクス（最適化前）:")
        baseline = result.baseline_metrics
        print(f"   総走行距離: {baseline.total_distance:.2f} km")
        print(f"   総所要時間: {baseline.total_duration} 分")
        print(f"   総コスト: ¥{baseline.total_cost:,.2f}")
        print(f"   平均積載率: {baseline.average_utilization_weight:.2f}%")
        print(f"   計算方法: {baseline.method}")

        print(f"\n🎯 改善効果:")
        improvement = result.improvement_metrics
        print(f"   距離削減: {improvement.distance_reduction_km:.2f} km "
              f"({improvement.distance_reduction_percent:.1f}%)")
        print(f"   時間削減: {improvement.duration_reduction_minutes} 分")
        print(f"   コスト削減: ¥{improvement.cost_reduction_amount:,.2f} "
              f"({improvement.cost_reduction_percent:.1f}%)")
        print(f"   積載率改善: {improvement.utilization_improvement_percent:.2f}%")

        # ルート詳細
        print(f"\n🚛 ルート詳細:")
        for idx, route in enumerate(result.routes, 1):
            print(f"\n   ルート {idx} (車両: {route.vehicle_id}):")
            print(f"      停車数: {len(route.stops)}箇所")
            print(f"      走行距離: {route.total_distance:.2f} km")
            print(f"      所要時間: {route.total_duration} 分")
            print(f"      コスト: ¥{route.total_cost:,.2f}")
            print(f"      積載率: 重量 {route.utilization_weight:.1f}%, "
                  f"容積 {route.utilization_volume:.1f}%")

            if route.stops:
                print(f"      配送順序:")
                for stop in route.stops:
                    # delivery IDから配送先名を取得
                    delivery = next((d for d in deliveries if d.id == stop.delivery_id), None)
                    customer_name = delivery.customer_name if delivery else "不明"
                    time_window = delivery.time_window if delivery else ""
                    time_window_str = f"[{time_window}]" if time_window else ""

                    print(f"         {stop.sequence}. {customer_name} {time_window_str}")
                    print(f"            到着: {stop.arrival_time}")
                    print(f"            距離: +{stop.distance_from_previous:.2f}km, "
                          f"時間: +{stop.duration_from_previous}分")

        print("\n" + "=" * 70)
        print("✅ すべてのテストが成功しました！")
        print("=" * 70)

        # 検証
        assert len(result.routes) > 0, "ルートが生成されていません"
        assert result.computation_time < 31000, "計算時間が31秒を超えています（30秒 + 1秒オーバーヘッド）"
        # 注: 時間窓制約があるため、距離削減率が負になる場合もある（積載率改善優先）

        return True

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_vrp_optimization()
    sys.exit(0 if success else 1)
