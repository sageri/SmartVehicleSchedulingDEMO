"""
Epic 005 Story 5.2 - 双重容量约束验证测试

验证 VRP Service 正确实现了重量和容积的双重容量约束
"""

import pytest
from datetime import time

from app.services.vrp_service import VRPService
from app.models.depot import Depot
from app.models.vehicle import Vehicle
from app.models.delivery import Delivery


class TestDualCapacityConstraints:
    """双重容量约束核心功能验证"""

    def test_data_model_has_dual_capacity_arrays(self):
        """
        验证 _create_data_model() 生成了重量和容积的独立数据数组
        """
        vrp_service = VRPService()

        # 创建测试数据
        depot = Depot(
            id="depot-test",
            name="テストデポ",
            latitude=35.6812,
            longitude=139.7671,
            address="東京",
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )

        vehicle = Vehicle(
            id="vehicle-test",
            depot_id="depot-test",
            vehicle_type="2t",
            capacity_weight=2000,
            capacity_volume=10.0,
            cost_per_km=50,
            cost_per_hour=2000,
        )

        deliveries = [
            Delivery(
                id="delivery-001",
                customer_name="顧客A",
                latitude=35.69,
                longitude=139.77,
                address="東京",
                package_count=1,
                weight=500.0,  # 500kg
                volume=2.5,    # 2.5m³
                time_window="morning",
                service_time=15,
            ),
            Delivery(
                id="delivery-002",
                customer_name="顧客B",
                latitude=35.68,
                longitude=139.76,
                address="東京",
                package_count=1,
                weight=300.0,  # 300kg
                volume=1.5,    # 1.5m³
                time_window="afternoon",
                service_time=10,
            ),
        ]

        # データモデル作成
        data = vrp_service._create_data_model([depot], [vehicle], deliveries)

        # 検証: demands_weight と demands_volume が存在すること
        assert "demands_weight" in data, "demands_weight が存在しません"
        assert "demands_volume" in data, "demands_volume が存在しません"

        # 検証: vehicle_capacities_weight と vehicle_capacities_volume が存在すること
        assert "vehicle_capacities_weight" in data, "vehicle_capacities_weight が存在しません"
        assert "vehicle_capacities_volume" in data, "vehicle_capacities_volume が存在しません"

        # 検証: demands の内容が正しいこと
        num_depots = 1
        assert data["demands_weight"][0] == 0, "拠点の重量需要は0であるべき"
        assert data["demands_weight"][1] == 500, "配送先1の重量需要は500kg"
        assert data["demands_weight"][2] == 300, "配送先2の重量需要は300kg"

        assert data["demands_volume"][0] == 0, "拠点の容積需要は0であるべき"
        assert data["demands_volume"][1] == 250, "配送先1の容積需要は2.5m³ = 250"
        assert data["demands_volume"][2] == 150, "配送先2の容積需要は1.5m³ = 150"

        # 検証: vehicle_capacities の内容が正しいこと
        assert data["vehicle_capacities_weight"][0] == 2000, "車両の重量容量は2000kg"
        assert data["vehicle_capacities_volume"][0] == 1000, "車両の容積容量は10.0m³ = 1000"

    def test_volume_constraint_prevents_overload(self):
        """
        容積制約が正しく機能し、容積超過を防ぐことを検証

        シナリオ:
        - 車両容量: 重量2000kg、容積5.0m³
        - 配送先A: 重量500kg、容積3.0m³
        - 配送先B: 重量600kg、容積3.0m³

        期待結果:
        - 重量合計1100kg（容量内）だが、容積合計6.0m³（容量超過）
        - VRPソルバーは A と B を同じルートに割り当てない
        """
        vrp_service = VRPService()

        depot = Depot(
            id="depot-test",
            name="テストデポ",
            latitude=35.6812,
            longitude=139.7671,
            address="東京",
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )

        # 2台の車両（容積制約を厳しくテスト）
        vehicles = [
            Vehicle(
                id="vehicle-001",
                depot_id="depot-test",
                vehicle_type="2t",
                capacity_weight=2000,
                capacity_volume=5.0,  # 容積が小さい
                cost_per_km=50,
                cost_per_hour=2000,
            ),
            Vehicle(
                id="vehicle-002",
                depot_id="depot-test",
                vehicle_type="2t",
                capacity_weight=2000,
                capacity_volume=5.0,
                cost_per_km=50,
                cost_per_hour=2000,
            ),
        ]

        deliveries = [
            Delivery(
                id="delivery-A",
                customer_name="顧客A（容積大）",
                latitude=35.69,
                longitude=139.77,
                address="東京",
                package_count=1,
                weight=500.0,   # 重量は軽い
                volume=3.0,     # 容積が大きい
                time_window=None,
                service_time=15,
            ),
            Delivery(
                id="delivery-B",
                customer_name="顧客B（容積大）",
                latitude=35.68,
                longitude=139.76,
                address="東京",
                package_count=1,
                weight=600.0,   # 重量は軽い
                volume=3.0,     # 容積が大きい
                time_window=None,
                service_time=10,
            ),
        ]

        # VRP最適化実行
        result = vrp_service.optimize([depot], vehicles, deliveries)

        # 検証: ルートが生成されること
        assert len(result.routes) > 0, "ルートが生成されていません"

        # 検証: 各ルートの容積が5.0m³以下であること
        for route in result.routes:
            assert route.total_volume <= 5.0, (
                f"ルート {route.id} の容積 {route.total_volume}m³ が"
                f"車両容量 5.0m³ を超えています"
            )

        # 検証: A と B が同じルートに割り当てられていないこと
        for route in result.routes:
            stop_delivery_ids = [stop.delivery_id for stop in route.stops]
            has_both_a_and_b = ("delivery-A" in stop_delivery_ids and
                               "delivery-B" in stop_delivery_ids)
            assert not has_both_a_and_b, (
                f"配送先A（3.0m³）と配送先B（3.0m³）が同じルートに割り当てられています。"
                f"容積合計6.0m³が車両容量5.0m³を超えるため、これは容積制約違反です。"
            )

    def test_weight_constraint_prevents_overload(self):
        """
        重量制約が正しく機能し、重量超過を防ぐことを検証

        シナリオ:
        - 車両容量: 重量1000kg、容積20.0m³
        - 配送先C: 重量700kg、容積1.0m³
        - 配送先D: 重量700kg、容積1.0m³

        期待結果:
        - 容積合計2.0m³（容量内）だが、重量合計1400kg（容量超過）
        - VRPソルバーは C と D を同じルートに割り当てない
        """
        vrp_service = VRPService()

        depot = Depot(
            id="depot-test",
            name="テストデポ",
            latitude=35.6812,
            longitude=139.7671,
            address="東京",
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )

        vehicles = [
            Vehicle(
                id="vehicle-001",
                depot_id="depot-test",
                vehicle_type="2t",
                capacity_weight=1000,  # 重量が小さい
                capacity_volume=20.0,
                cost_per_km=50,
                cost_per_hour=2000,
            ),
            Vehicle(
                id="vehicle-002",
                depot_id="depot-test",
                vehicle_type="2t",
                capacity_weight=1000,
                capacity_volume=20.0,
                cost_per_km=50,
                cost_per_hour=2000,
            ),
        ]

        deliveries = [
            Delivery(
                id="delivery-C",
                customer_name="顧客C（重量大）",
                latitude=35.69,
                longitude=139.77,
                address="東京",
                package_count=1,
                weight=700.0,   # 重量が大きい
                volume=1.0,     # 容積は小さい
                time_window=None,
                service_time=15,
            ),
            Delivery(
                id="delivery-D",
                customer_name="顧客D（重量大）",
                latitude=35.68,
                longitude=139.76,
                address="東京",
                package_count=1,
                weight=700.0,   # 重量が大きい
                volume=1.0,     # 容積は小さい
                time_window=None,
                service_time=10,
            ),
        ]

        # VRP最適化実行
        result = vrp_service.optimize([depot], vehicles, deliveries)

        # 検証: ルートが生成されること
        assert len(result.routes) > 0, "ルートが生成されていません"

        # 検証: 各ルートの重量が1000kg以下であること
        for route in result.routes:
            assert route.total_weight <= 1000, (
                f"ルート {route.id} の重量 {route.total_weight}kg が"
                f"車両容量 1000kg を超えています"
            )

        # 検証: C と D が同じルートに割り当てられていないこと
        for route in result.routes:
            stop_delivery_ids = [stop.delivery_id for stop in route.stops]
            has_both_c_and_d = ("delivery-C" in stop_delivery_ids and
                               "delivery-D" in stop_delivery_ids)
            assert not has_both_c_and_d, (
                f"配送先C（700kg）と配送先D（700kg）が同じルートに割り当てられています。"
                f"重量合計1400kgが車両容量1000kgを超えるため、これは重量制約違反です。"
            )

    def test_dual_constraints_work_together(self):
        """
        重量と容積の制約が同時に機能することを検証

        シナリオ:
        - 車両容量: 重量1500kg、容積8.0m³
        - 配送先E: 重量800kg、容積2.0m³  → OK単独
        - 配送先F: 重量600kg、容積5.0m³  → OK単独
        - 配送先G: 重量700kg、容積3.0m³  → OK単独

        組み合わせ制約:
        - E + F: 重量1400kg（OK）、容積7.0m³（OK） → 可能
        - E + G: 重量1500kg（OK）、容積5.0m³（OK） → 可能
        - F + G: 重量1300kg（OK）、容積8.0m³（OK） → 可能
        - E + F + G: 重量2100kg（NG）、容積10.0m³（NG） → 不可能
        """
        vrp_service = VRPService()

        depot = Depot(
            id="depot-test",
            name="テストデポ",
            latitude=35.6812,
            longitude=139.7671,
            address="東京",
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )

        vehicles = [
            Vehicle(
                id="vehicle-001",
                depot_id="depot-test",
                vehicle_type="2t",
                capacity_weight=1500,
                capacity_volume=8.0,
                cost_per_km=50,
                cost_per_hour=2000,
            ),
            Vehicle(
                id="vehicle-002",
                depot_id="depot-test",
                vehicle_type="2t",
                capacity_weight=1500,
                capacity_volume=8.0,
                cost_per_km=50,
                cost_per_hour=2000,
            ),
        ]

        deliveries = [
            Delivery(
                id="delivery-E",
                customer_name="顧客E",
                latitude=35.69,
                longitude=139.77,
                address="東京",
                package_count=1,
                weight=800.0,
                volume=2.0,
                time_window=None,
                service_time=15,
            ),
            Delivery(
                id="delivery-F",
                customer_name="顧客F",
                latitude=35.68,
                longitude=139.76,
                address="東京",
                package_count=1,
                weight=600.0,
                volume=5.0,
                time_window=None,
                service_time=10,
            ),
            Delivery(
                id="delivery-G",
                customer_name="顧客G",
                latitude=35.67,
                longitude=139.75,
                address="東京",
                package_count=1,
                weight=700.0,
                volume=3.0,
                time_window=None,
                service_time=12,
            ),
        ]

        # VRP最適化実行
        result = vrp_service.optimize([depot], vehicles, deliveries)

        # 検証: ルートが生成されること
        assert len(result.routes) > 0, "ルートが生成されていません"

        # 検証: 各ルートが両方の容量制約を満たすこと
        for route in result.routes:
            assert route.total_weight <= 1500, (
                f"ルート {route.id} の重量 {route.total_weight}kg が"
                f"車両容量 1500kg を超えています"
            )
            assert route.total_volume <= 8.0, (
                f"ルート {route.id} の容積 {route.total_volume}m³ が"
                f"車両容量 8.0m³ を超えています"
            )

        # 検証: E, F, G の3つすべてが同じルートに割り当てられていないこと
        for route in result.routes:
            stop_delivery_ids = [stop.delivery_id for stop in route.stops]
            has_all_three = (
                "delivery-E" in stop_delivery_ids and
                "delivery-F" in stop_delivery_ids and
                "delivery-G" in stop_delivery_ids
            )
            assert not has_all_three, (
                f"配送先E, F, Gの3つすべてが同じルートに割り当てられています。"
                f"合計: 重量2100kg（容量1500kg超過）、容積10.0m³（容量8.0m³超過）"
            )


class TestBackwardCompatibility:
    """後方互換性テスト - 既存のテストが引き続き動作することを確認"""

    def test_existing_tests_still_work(self):
        """
        既存の test_vrp_service.py のような単一容量制約テストが引き続き動作することを確認
        """
        vrp_service = VRPService()

        depot = Depot(
            id="depot-tokyo",
            name="東京デポ",
            latitude=35.6812,
            longitude=139.7671,
            address="東京",
            operating_start_time=time(8, 0),
            operating_end_time=time(18, 0),
        )

        vehicles = [
            Vehicle(
                id="vehicle-001",
                depot_id="depot-tokyo",
                vehicle_type="2t",
                capacity_weight=2000.0,
                capacity_volume=8.0,
                cost_per_km=50.0,
                cost_per_hour=2000.0,
            ),
        ]

        deliveries = [
            Delivery(
                id="delivery-001",
                customer_name="新宿商店A",
                latitude=35.6895,
                longitude=139.6917,
                address="東京",
                package_count=2,
                weight=150.0,
                volume=0.5,
                time_window="morning",
                service_time=15,
            ),
        ]

        # VRP最適化実行（エラーが出ないことを確認）
        result = vrp_service.optimize([depot], vehicles, deliveries)

        # 基本検証
        assert len(result.routes) > 0, "ルートが生成されていません"
        assert result.total_distance > 0, "総走行距離が計算されていません"
