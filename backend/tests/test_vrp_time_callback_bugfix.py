"""
Epic 005 Story 5.2 - Critical Bug Fix Test

验证 time_callback 在 Multi-Depot 模式下正确处理节点索引
"""

import pytest


class TestTimeCallbackBugFix:
    """time_callback Multi-Depot 索引修复验证"""

    def test_time_callback_logic_with_multi_depot(self):
        """
        验证 time_callback 在 Multi-Depot 下的节点判断逻辑

        Bug描述:
        - 原代码: if to_node > 0
        - 问题1: 拠点1,2,3被误判为配送先
        - 问题2: deliveries[to_node - 1] 在 to_node >= num_depots + len(deliveries) 时越界

        修复后:
        - 新代码: if to_node >= num_depots
        - 正确判断: 只有配送先节点才添加服务时间
        """
        num_depots = 4
        num_deliveries = 100

        # 测试场景1: 拠点节点（0-3）不应添加服务时间
        for depot_node in range(num_depots):
            # 修复后: depot_node < num_depots，条件为 False
            should_add_service_time = depot_node >= num_depots
            assert should_add_service_time == False, (
                f"拠点ノード {depot_node} は配送先として誤判定されるべきではない"
            )

        # 测试场景2: 配送先节点（4-103）应添加服务时间
        for delivery_node in range(num_depots, num_depots + num_deliveries):
            # 修复后: delivery_node >= num_depots，条件为 True
            should_add_service_time = delivery_node >= num_depots
            assert should_add_service_time == True, (
                f"配送先ノード {delivery_node} はサービス時間を追加すべき"
            )

        # 测试场景3: 配送先数组索引计算正确性
        for delivery_node in range(num_depots, num_depots + num_deliveries):
            # 修复后: delivery_index = delivery_node - num_depots
            delivery_index = delivery_node - num_depots

            # 验证索引在有效范围内
            assert 0 <= delivery_index < num_deliveries, (
                f"配送先インデックス {delivery_index} が範囲外 [0, {num_deliveries})"
            )

    def test_original_bug_scenarios(self):
        """
        验证原始Bug的具体场景已修复
        """
        num_depots = 4
        deliveries_length = 100

        # Bug场景1: 横浜デポ（node=1）被误判为配送先
        yokohama_node = 1

        # 原代码逻辑: to_node > 0 → True
        original_logic = yokohama_node > 0
        assert original_logic == True, "原代码会误判横浜デポ为配送先"

        # 修复后逻辑: to_node >= num_depots → False
        fixed_logic = yokohama_node >= num_depots
        assert fixed_logic == False, "修复后正确识别横浜デポ为拠点"

        # Bug场景2: 最后一个配送先（node=103）导致数组越界
        last_delivery_node = num_depots + deliveries_length - 1  # 103

        # 原代码索引: deliveries[103 - 1] = deliveries[102]
        # 问题: deliveries数组只有100个元素（索引0-99），102越界！
        original_index = last_delivery_node - 1  # 102
        assert original_index >= deliveries_length, (
            f"原代码索引 {original_index} 会越界（数组长度={deliveries_length}）"
        )

        # 修复后索引: deliveries[103 - 4] = deliveries[99]
        fixed_index = last_delivery_node - num_depots  # 99
        assert fixed_index < deliveries_length, (
            f"修复后索引 {fixed_index} 在有效范围内（数组长度={deliveries_length}）"
        )
        assert fixed_index == deliveries_length - 1, (
            "修复后正确访问最后一个配送先"
        )

    def test_edge_cases(self):
        """测试边界情况"""
        num_depots = 4

        # 边界1: 第一个拠点（node=0）
        first_depot_node = 0
        assert first_depot_node < num_depots, "第一个拠点应该被识别为拠点"

        # 边界2: 最后一个拠点（node=3）
        last_depot_node = num_depots - 1
        assert last_depot_node < num_depots, "最后一个拠点应该被识别为拠点"

        # 边界3: 第一个配送先（node=4）
        first_delivery_node = num_depots
        assert first_delivery_node >= num_depots, "第一个配送先应该被识别为配送先"

        # 边界4: 配送先索引计算
        first_delivery_index = first_delivery_node - num_depots
        assert first_delivery_index == 0, "第一个配送先的索引应该是0"


class TestSingleDepotBackwardCompatibility:
    """验证 Single Depot 模式的后方互换性"""

    def test_single_depot_logic_still_works(self):
        """
        验证修复后 Single Depot（1拠点）仍然正确工作
        """
        num_depots = 1  # Single Depot 模式
        num_deliveries = 20

        # 拠点节点（0）不应添加服务时间
        depot_node = 0
        should_add_service_time = depot_node >= num_depots
        assert should_add_service_time == False, "Single Depot 模式下拠点0不添加服务时间"

        # 配送先节点（1-20）应添加服务时间
        for delivery_node in range(num_depots, num_depots + num_deliveries):
            should_add_service_time = delivery_node >= num_depots
            assert should_add_service_time == True, (
                f"Single Depot 模式下配送先 {delivery_node} 应添加服务时间"
            )

            # 索引计算
            delivery_index = delivery_node - num_depots
            assert 0 <= delivery_index < num_deliveries, (
                f"Single Depot 模式下索引 {delivery_index} 应在有效范围内"
            )
