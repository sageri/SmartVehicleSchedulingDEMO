# ADR 002: Multi-Depot VRP实现决策

**状态:** ✅ 已接受并实施（Epic 005）
**日期:** 2025-11-03
**决策者:** 开发团队
**上下文来源:** Epic 005 - Demo Data Expansion

---

## 上下文 (Context)

Epic 005目标是将Demo系统从单拠点扩展至Multi-Depot场景：

**现状（Epic 005前）:**
- 1拠点（东京）、20配送先、3台車両
- 所有车辆从同一拠点出发和返回
- VRP求解时间约30秒

**需求:**
- 2拠点（东京 + 第二拠点）
- 30配送先（东京20件 + 第二拠点10件）
- 5台車両（东京3台 + 第二拠点2台）
- **关键约束:** 各车辆只能配送所属拠点的配送先

---

## 决策 (Decision)

### 决策1: 拠点制约实现方式

**选择方案1：OR-Tools `SetAllowedVehiclesForIndex` API**

实施为：
```python
# backend/app/services/vrp_service.py
for delivery_index, delivery in enumerate(deliveries):
    # 找出可以配送此点的车辆（同拠点）
    depot_vehicles = [v for v in vehicles if v.depot_id == delivery.depot_id]
    allowed_vehicle_indices = [vehicles.index(v) for v in depot_vehicles]

    # 设置OR-Tools拠点制约
    routing.SetAllowedVehiclesForIndex(
        allowed_vehicle_indices,
        delivery_index + num_depots
    )
```

---

### 决策2: 第二拠点位置选择

**最终选择：さいたま市（埼玉県）**

经历2次调整：
1. **初期计划:** 横浜市（Story 5.1）
2. **Story 5.1.1调整:** さいたま市

**选择さいたま市的理由:**
- ✅ **陆地稳定性:** 距离海岸较远，避免配送点落海
- ✅ **距离适中:** 距东京约20km，两拠点独立性好
- ✅ **实在地点丰富:** さいたま新都心、浦和駅等知名地点
- ⚠️ 横浜被放弃原因: 靠近海岸，随机生成配送点易落海

---

### 决策3: 配送点生成方式

**选择方案2：固定配送点列表（实在地点）**

废除Story 5.1的随机生成方式，改为：

```python
# backend/app/api/v1/seed.py
FIXED_DELIVERY_LOCATIONS = {
    "depot-tokyo": [
        {"name": "新宿区役所", "latitude": 35.6938, "longitude": 139.7034},
        {"name": "渋谷駅周辺", "latitude": 35.6580, "longitude": 139.7016},
        # ... 20件
    ],
    "depot-saitama": [
        {"name": "さいたま新都心", "latitude": 35.8908, "longitude": 139.6303},
        {"name": "浦和駅周辺", "latitude": 35.8616, "longitude": 139.6566},
        # ... 10件
    ]
}
```

**为什么从随机生成改为固定列表:**
- ❌ 随机生成（Story 5.1）: 即使加bearing制约，仍有5-10%配送点落海
- ✅ 固定列表（Story 5.1.1）: 100%陆地，Demo时显示实在地名

---

## 理由 (Rationale)

### 为什么选择OR-Tools `SetAllowedVehiclesForIndex`

**优点:**
1. **原生支持:** OR-Tools官方Multi-Depot VRP API
2. **强制约束:** Solver无法生成违反拠点制约的解
3. **性能稳定:** 不影响求解时间（测试验证）
4. **实现简单:** 仅需15行代码

**与备选方案对比:**

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **SetAllowedVehiclesForIndex** | 原生支持、强制约束 | 需理解OR-Tools API | ✅ 选择 |
| 自定义Constraint Callback | 灵活性高 | 实现复杂、性能差 | ❌ |
| 后处理过滤 | 实现简单 | 无法保证有解 | ❌ |

---

### 为什么选择さいたま市而非横浜

**数据分析（Story 5.1.1）:**
- 横浜随机生成：5-10%配送点落海（东京湾）
- さいたま市随机生成：0%配送点落海（内陆）

**进一步决策（Story 5.1.1）:**
- 即使さいたま市随机生成成功率高，仍选择固定列表（100%保证）

---

### 为什么选择固定配送点列表

**对比随机生成的优势:**

| 维度 | 随机生成 | 固定列表 | 结果 |
|------|---------|---------|------|
| 陆地保证 | 90-95% | 100% | ✅ 固定 |
| Demo真实感 | 低（随机地名） | 高（实在地名） | ✅ 固定 |
| 可复现性 | 每次不同 | 完全一致 | ✅ 固定 |
| 国际化 | 容易 | 困难 | ⚠️ 权衡 |
| 维护成本 | 低 | 中 | ⚠️ 权衡 |

**Demo场景下的最终判断:**
- ✅ Demo真实感 > 国际化灵活性
- ✅ 100%陆地保证 > 随机性

---

## 后果 (Consequences)

### 正面影响

**技术成果:**
- ✅ Multi-Depot VRP成功实现（Story 5.2）
- ✅ 両拠点均生成稳定路径
- ✅ 拠点制约100%有效（验证通过）
- ✅ 配送点海上问题完全解消（0件）

**业务价值:**
- ✅ 中规模Demo説得力向上（30配送先 vs 20配送先）
- ✅ 实在地名提升Demo专业性
- ✅ Multi-Depot场景覆盖更多业务需求

### 负面影响及应对

**1. 固定配送点的局限性**
- ❌ 问题: 配送点硬编码在`seed.py`，国际化困难
- ✅ 应对: 未来可迁移至JSON文件或DB表（推荐改进）

**2. 拠点扩展性**
- ❌ 问题: 当前仅2拠点，3拠点以上未测试
- ✅ 应对: 架构支持N拠点，Epic 006可测试3-4拠点

**3. 距离矩阵大小**
- ❌ 问题: 2拠点+30配送先=32节点，距离矩阵32×32
- ✅ 应对: OR-Tools可支持100+节点，性能无问题

---

## 实施细节

### 数据模型扩展
```python
# backend/app/models/delivery.py (Story 5.1.1)
class Delivery(Base):
    # ... existing fields ...
    depot_id = Column(String, ForeignKey("depots.id"), nullable=False, index=True)
    # ★ 新增字段：关联拠点
```

### VRP拠点制约实现
```python
# backend/app/services/vrp_service.py (Story 5.2)
# 1. 创建Multi-Depot距离矩阵（2拠点 + 30配送先 = 32节点）
distance_matrix = self._create_distance_matrix(depots, deliveries)

# 2. 设置車両起终点
starts = [depots.index(vehicle.depot) for vehicle in vehicles]  # [0,0,0,1,1]
ends = starts  # 返回同一拠点

# 3. 创建Routing Model
routing = pywrapcp.RoutingModel(len(distance_matrix), len(vehicles), starts, ends)

# 4. 设置拠点制约
for delivery_index, delivery in enumerate(deliveries):
    depot_vehicles = [v for v in vehicles if v.depot_id == delivery.depot_id]
    allowed_vehicle_indices = [vehicles.index(v) for v in depot_vehicles]
    routing.SetAllowedVehiclesForIndex(
        allowed_vehicle_indices,
        delivery_index + num_depots  # +2 offset
    )
```

### 固定配送点实施
```python
# backend/app/api/v1/seed.py (Story 5.1.1)
for depot_config in DEPOT_CONFIGS:
    depot_id = depot_config["id"]
    delivery_count = DELIVERIES_PER_DEPOT[depot_id]

    # 从固定列表随机选择指定数量
    selected_locations = random.sample(
        FIXED_DELIVERY_LOCATIONS[depot_id],
        delivery_count
    )

    for loc in selected_locations:
        delivery = Delivery(
            id=f"delivery-{delivery_counter:03d}",
            customer_name=loc["name"],
            latitude=loc["latitude"],
            longitude=loc["longitude"],
            depot_id=depot_id,  # ★ 关联拠点
            # ... other fields ...
        )
```

---

## 验证结果

### Story 5.1验证（2025-11-03）
- ✅ 2拠点数据正常生成（东京、横浜）
- ⚠️ 配送点海上问题：横浜周边5-10%点落海

### Story 5.1.1验证（2025-11-04）
- ✅ 2拠点数据正常生成（东京、さいたま市）
- ✅ 配送点海上问题完全解消（0件）
- ✅ 30件配送先depot_id正确分配

### Story 5.2验证（2025-11-04）
- ✅ Multi-Depot VRP成功完成（10-60秒）
- ✅ 拠点制约验证：东京車両仅访问东京配送先
- ✅ 拠点制约验证：さいたま市車両仅访问さいたま市配送先
- ✅ 両拠点均生成有效路径

---

## 备选方案分析

### 方案1: 软制约（Penalty-based）
**思路:** 不强制拠点制约，而是对跨拠点配送添加高额penalty

**为什么不选:**
- ❌ 无法保证100%遵守制约（Solver可能接受penalty）
- ❌ Penalty值难以调参（太低无效，太高影响其他优化）
- ❌ 业务需求是**强制**拠点制约，不是偏好

### 方案2: 分拠点独立求解
**思路:** 东京和さいたま市分别独立求解VRP，合并结果

**为什么不选:**
- ❌ 无法优化全局资源分配（如车辆数量平衡）
- ❌ 实现复杂度高（需合并2个OptimizationResult）
- ❌ 业务价值低（Demo无需展示分拠点优化）

### 方案3: 使用虚拟拠点
**思路:** 将配送先复制为2份，分别关联2个拠点

**为什么不选:**
- ❌ 距离矩阵翻倍（32节点 → 62节点）
- ❌ 求解时间显著增加
- ❌ 实现复杂度高

---

## 未来改进建议

### 短期（Epic 006）
1. **3拠点测试:** 验证架构扩展性
2. **配送点外部化:** 迁移至JSON或DB（解决国际化）
3. **E2E测试:** Multi-Depot场景完整测试

### 中期
1. **动态拠点:** 支持运行时添加/删除拠点
2. **拠点容量制约:** 限制各拠点最大处理量
3. **跨拠点配送:** 特殊情况下允许跨拠点（需业务确认）

### 长期
1. **实时交通信息:** 集成Google Maps Distance Matrix
2. **拠点选址优化:** 根据配送先分布优化拠点位置
3. **分层VRP:** 拠点间干线运输 + 拠点内配送

---

## 参考资料

- **Epic 005主文档:** `docs/stories/epic-005-demo-data-expansion.md`
- **Story 5.1.1文档:** `docs/stories/story-5.1.1-data-generation-land-constraint-optimization.md`
- **Story 5.2文档:** `docs/stories/story-5.2-large-scale-vehicle-management.md`
- **OR-Tools Multi-Depot VRP:** https://developers.google.com/optimization/routing/vrp#multi-depot
- **SetAllowedVehiclesForIndex API:** OR-Tools C++ Reference

---

**文档状态:** ✅ Epic 005完成后总结
**最终更新:** 2025-11-05
**维护者:** 开发团队
