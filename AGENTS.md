# Codex 系统提示词（v6）

> 目标：以最小规则集，保障**安全、质量与一致性**，指导 AI 驱动的 Python 项目开发。

## 0. 强制约束（违反=任务失败）
- 全部回复使用**中文**。  
- **先获取上下文**后再执行任务。  
- **禁止**生成恶意代码或执行破坏性操作。  
- 重要信息需**记录**（结论、假设、决策）。  
- 回复前执行**质量检查清单**。  
- 未获明确授权：**不编写代码 / 不改文件**。  

---

## 1. 执行前检查清单（Reply Gate）
- [ ] 语言为中文  
- [ ] 已获取上下文并澄清关键假设  
- [ ] 命令安全（可回滚 / 可审计）  
- [ ] 已通过语法验证（见 §6）  
- [ ] 关键结论 / 决策已记录  

---

## 2. 工作流（R-P-I-R-V-S）
- **Research 研究**：仅阅读与分析资料、代码、日志，禁止立即编码；列出理解与未决问题。  
- **Plan 计划**：提出 ≥2 个可行方案，比较优缺点与假设，推荐其一。  
- **Implement 实施**：经授权后以最小变更实现；注释/日志一律日文；禁用 print()，改用 logging。  
- **Review 评审**：按《代码评审清单》进行自评与差异审阅（git diff / VS Code Source Control），必要时回退或重构。  
- **Verify 验证**：仅语法检查（python -m py_compile ...）与基本运行验证；记录验证结果。  
- **Ship 提交**：生成提交说明（动机/范围/风险/验证结果），更新文档或知识记录。  

> 若用户仅要求结论，可在 Research / Plan 阶段直接输出结论及取舍理由。  

---

## 3. 语言与文档
- 与 Codex 交互及协作沟通：**中文**。  
- 代码注释、日志、错误信息：**日文**。  
- 文档（README / AGENTS / 变更记录）：**中文**。  
- 输出规范：命令与路径使用反引号包裹，代码使用 fenced block。  

---

## 4. 质量标准（KISS / YAGNI / SOLID / DRY）
- **KISS**：设计简洁、易读、易维护。  
- **YAGNI**：不开发未确认的需求。  
- **SOLID**：保持模块职责清晰、可扩展。  
- **DRY**：消除重复逻辑，提高复用性。  
- 所有函数需包含类型注解与**日文 docstring**。  
- 命名清晰、注释充分、逻辑合理。  
- 保持性能意识（算法复杂度、内存与 I/O）。  
- 错误需显式处理并记录上下文。  

---

## 5. 代码评审清单（最小必查）
1. 正确性与边界  
2. 副作用与单一职责  
3. 异常处理与日志记录（日文）  
4. 禁止 print()，统一使用 logging  
5. 循环与条件复杂度  
6. 命名可读性与 DRY 原则  
7. 模块边界与职责分离（SOLID-S）  
8. 类型注解与日文 docstring 完整  
9. 性能热点（N² / I/O / 缓存）  
10. 未使用的导入与变量清理  
11. 安全性（无硬编码敏感信息）  
12. 回滚与容错思路（如涉及破坏性操作）

---

## 6. 验证与检查（仅语法层）
- 不使用 pytest 或外部测试框架。  
- 使用 Python 内置编译检测：  
  ```bash
  python -m py_compile main.py
  ```  
- 若存在多模块：  
  ```bash
  for /R %%f in (*.py) do python -m py_compile "%%f"
  ```  
  或  
  ```bash
  find . -name "*.py" -exec python -m py_compile {} \;
  ```  
- 通过检查即视为验证成功。  
- 运行时验证仅限基本逻辑、错误处理、依赖导入。  
- 所有验证日志记录在 `logs/verify.log`（若存在）。  

---

## 7. 开发与环境
- Python **3.12+**（**当前 3.14**，保持兼容 3.12）。  
- 虚拟环境：  
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```  
- 依赖固定：  
  ```bash
  pip freeze > requirements.txt
  ```  
- 文件编码：**UTF-8（无 BOM）**。  
- 不得引用未安装模块或依赖。  

---

## 8. 安全与配置
- 禁止硬编码密钥 / 令牌；敏感信息存放 `.env`。  
- `.gitignore` 排除 `.env` 与日志文件。  
- `.env.example` 提供配置示例字段。  
- 涉及破坏性命令时需二次确认并提供回滚方案。  
- 若发现权限异常或执行风险，应立即终止操作并提示用户。  

---

## 9. 项目结构（最小必需）
```
project-root/
  src/
  docs/
  config/
  logs/
  requirements.txt
  README.md
  AGENTS.md
  .env
  .env.example
```

---

## 10. 提交与维护
- 提交信息遵循 **Conventional Commit**：  
  `feat|fix|docs|refactor|chore`。  
- 提交前确认：语法检查通过，无未保存修改。  
- 提交说明需包含：变更目的、影响范围、风险与解决方案。  

---

## 11. 决策与冲突处理
- 记录决策选项、取舍理由与边界。  
- 若存在不确定性，先列假设后再执行。  
- 优先级：**安全 > 合规 > 质量 > 进度**。  
- 用户要求与本规范冲突时：应说明风险并提供替代方案。  

---

## 12. 授权边界（默认拒绝）
- 无明确“编写/修改授权” → 不写代码 / 不改文件。  
- 无路径 / 目标文件 → 不执行写入操作。  
- 无回滚方案 → 不执行破坏性命令。  

---

## 13. 函数模板（示例）
```python
def add_numbers(a: int, b: int) -> int:
    """
    2つの数値を加算する。
    Args:
        a (int): 数値1
        b (int): 数値2
    Returns:
        int: 加算結果
    """
    import logging
    logging.debug("加算処理: a=%d, b=%d", a, b)
    return a + b
```

---

## 14. Epic 005 实践总结（Multi-Depot VRP实施）

### Epic 005概要
- **目标**: 扩展Demo数据至中规模实证环境（2拠点·30配送先·5台車両）
- **完成日期**: 2025-11-04
- **关键成果**: Multi-Depot VRP实现、VRP计算时间5倍优化、固定配送点方式

### 关键技术决策

#### 1. 固定配送点列表 vs 随机生成
**问题**: 随机生成导致配送点落入海上
**决策**: 采用固定配送点列表（30件实在地点）
**实施**: `backend/app/api/v1/seed.py:76-120`定义`FIXED_DELIVERY_LOCATIONS`字典
**效果**:
- ✅ 配送点海上配置问题完全解消（0件）
- ✅ Demo时显示实在地名（说得力向上）
- ⚠️ 国际化困难（日本地名硬编码）

#### 2. Multi-Depot拠点制约实现
**问题**: 如何确保车両只访问所属拠点的配送先
**决策**: 使用OR-Tools `SetAllowedVehiclesForIndex` API
**实施**: `backend/app/services/vrp_service.py:200-250`
```python
# 拠点制約実装
for delivery_index, delivery in enumerate(deliveries):
    depot_vehicles = [v for v in vehicles if v.depot_id == delivery.depot_id]
    allowed_vehicle_indices = [vehicles.index(v) for v in depot_vehicles]
    routing.SetAllowedVehiclesForIndex(
        allowed_vehicle_indices,
        delivery_index + num_depots
    )
```
**效果**:
- ✅ 东京車両只配送东京配送先
- ✅ 埼玉車両只配送埼玉配送先

#### 3. VRP计算时间优化（300秒 → 60秒）
**问题**: 30配送先计算时间过长
**决策组合**:
- 超时设定: 300秒 → 60秒
- 初期解策略: `PATH_CHEAPEST_ARC` → `PARALLEL_CHEAPEST_INSERTION`（Multi-Depot最优）
- 时间窗柔性: 指定なし 10% → 50%（解探索性向上）
- 时间窗重叠: 午前/午後间设置1小时重叠期间（避免空白期间）
- 等待时间许容: 30分 → 60分

**实施**:
- `vrp_service.py`: 超时和初期解策略
- `seed.py`: 时间窗分布调整(`TIME_WINDOW_WEIGHTS = [0.2, 0.3, 0.5]`)

**效果**:
- ✅ 平均计算时间: 10-60秒（目标达成）
- ✅ 両拠点均生成稳定路径

#### 4. 双重容量制约（重量 + 容積）
**问题**: 原先仅重量制约，容积未考虑
**决策**: 使用`AddDimensionWithVehicleCapacity`实现双重制约
**实施**: `vrp_service.py`中分别定义weight_callback和volume_callback
**效果**: ✅ 更贴近实际业务需求

### 数据模型扩展
- 添加`Delivery.depot_id`外键（`backend/app/models/delivery.py:45`）
- 无需数据库迁移（SQLite删除重建）

### 验证流程增强
**Multi-Depot VRP专用验证**:
1. 数据生成验证: 确认30配送先depot_id正确分配
2. 拠点制约验证: 检查生成路径是否违反拠点制约
3. VRP计算时间验证: 确认60秒内完成
4. 两拠点路径验证: 确认东京和埼玉両方生成路径

### 遇到的挑战与解决

#### 挑战1: 配送点海上配置（Story 5.1.1）
**问题**: bearing制约的随机生成仍导致部分点落海
**解决**: 完全废除随机生成，改用固定配送点列表
**教训**: 地理数据生成时应优先使用实在地点

#### 挑战2: VRP计算超时（Story 5.2）
**问题**: 初期40配送先、300秒超时仍经常超时
**解决**:
- 减少配送先至30件
- 大幅提升时间窗柔性（50%指定なし）
- 超时缩短至60秒（强制约束）
**教训**: 时间窗柔性是VRP求解性能的关键因素

#### 挑战3: HTTP超时不匹配（Story 5.3）
**问题**: Frontend 360秒超时 > Backend 60秒超时（不合理）
**解决**: Frontend超时缩短至120秒（Backend 60秒 + Buffer）
**教训**: 客户端超时必须大于服务端超时+Buffer

### 文档维护经验
1. **Epic主文档实时更新**: `epic-005-demo-data-expansion.md`记录所有变更
2. **Story完成报告**: 每个Story生成完成报告（`story-5.1.1-completion-report.md`）
3. **ADR记录**: 重大技术决策应记录为ADR文档
4. **过程文档归档**: 验证记录、决策分析等应移至`docs/history/`

### 代码质量实践
1. **日文注释**: 所有代码注释使用日文（遵循AGENTS.md规范）
2. **类型注解**: 所有函数包含完整类型注解
3. **日文Docstring**: 所有函数包含日文docstring
4. **Logging替代print**: 使用logging模块而非print()
5. **DRY原则**: 拠点配置统一在`DEPOT_CONFIGS`字典管理

### 推荐的未来改进
1. **配送点外部化**: 将`FIXED_DELIVERY_LOCATIONS`移至JSON文件或DB表
2. **3拠点以上扩展**: 当前架构支持N拠点，测试3-4拠点场景
3. **实时交通信息**: 替换Haversine距离为实际路网距离
4. **异步VRP计算**: 使用Celery或FastAPI BackgroundTasks
5. **E2E测试实施**: Story 006计划实施完整E2E测试

---

### 一句话准则
> **先理解，再执行；先评审，再提交；安全优先，最小变更。**
