# ADR 001: 同步API设计决策

**状态:** ✅ 已接受并实施
**日期:** 2025-11-02
**决策者:** 开发团队
**上下文来源:** Story 002 - Optimization Engine Implementation

---

## 上下文 (Context)

在实施Story 002时，需要决定VRP最适化API的架构模式：

**需求:**
- Demo系统需要简单、可靠的API
- VRP计算时间预计10-60秒（Epic 005后）
- Frontend需实时获取结果

**技术选项:**
1. **同步API**：HTTP请求直接等待计算完成
2. **异步API**：返回任务ID，轮询或WebSocket获取结果

---

## 决策 (Decision)

**选择方案1：同步API（Blocking HTTP）**

实施为：`POST /api/v1/optimization/optimize`
- 请求发送后，服务端立即开始VRP计算
- 连接保持打开状态，直到计算完成
- 返回完整的OptimizationResult对象

**超时设定:**
- Backend: 60秒（Epic 005优化后）
- Frontend: 120秒（包含Buffer）

---

## 理由 (Rationale)

### 优点
1. **实现简单:** 无需任务队列、状态管理、轮询逻辑
2. **代码量少:** Backend和Frontend都无需额外基础设施
3. **错误处理清晰:** HTTP超时即失败，无需追踪任务状态
4. **Demo场景适合:** 单用户、低并发、短计算时间
5. **开发速度快:** Story 002可在2天内完成

### 缺点及缓解
1. ❌ **连接占用:** 计算期间HTTP连接保持打开
   - ✅ 缓解: Demo系统单用户，无并发问题
2. ❌ **超时风险:** 计算时间>60秒会失败
   - ✅ 缓解: Epic 005优化计算时间至10-60秒
3. ❌ **无进度反馈:** 用户只能看到加载动画
   - ✅ 缓解: Story 5.3添加"VRP最適化実行中..."提示

---

## 备选方案 (Alternatives)

### 方案2: 异步API + 轮询
```
POST /optimize → {task_id}
GET /optimize/{task_id} → {status, result}
```

**为什么不选:**
- 需要任务队列（Celery/RQ）和状态存储（Redis）
- Frontend需轮询逻辑，增加复杂度
- Demo场景overengineering
- **开发时间:** 至少5天（vs 同步2天）

### 方案3: WebSocket实时推送
```
WebSocket连接 → 实时进度 + 最终结果
```

**为什么不选:**
- 需要WebSocket服务器和客户端实现
- FastAPI WebSocket需额外配置
- Demo场景不需要实时进度
- **开发时间:** 至少4天

---

## 后果 (Consequences)

### 正面影响
- ✅ Story 002按时完成（2天）
- ✅ 代码简洁易维护
- ✅ Demo演示流畅（10-60秒等待可接受）
- ✅ 错误处理直观（超时=失败）

### 负面影响及应对
- ⚠️ **不适合生产环境:**
  - 问题: 并发请求会占用大量连接
  - 应对: README中明确标注为Demo系统

- ⚠️ **扩展性受限:**
  - 问题: 100+配送先可能超时
  - 应对: Epic 005优化至60秒内完成30配送先

- ⚠️ **无法取消任务:**
  - 问题: 一旦开始计算，无法中途取消
  - 应对: Demo场景不需要此功能

### 未来改进路径
如果系统投入生产，建议：
1. 迁移至异步API + Celery任务队列
2. 添加WebSocket实时进度推送
3. 实现任务取消功能
4. 使用Redis缓存计算结果

---

## 实施细节

### Backend实现
```python
# backend/app/api/v1/optimization.py
@router.post("/optimize", response_model=OptimizationResult)
async def optimize_routes(request: OptimizationRequest, db: Session = Depends(get_db)):
    # 直接调用VRP服务（同步）
    result = vrp_service.optimize(request, db)
    return result
```

### Frontend实现
```typescript
// frontend/src/services/api.ts
export const optimizeRoutes = async (request: OptimizationRequest) => {
  const response = await axios.post('/api/v1/optimization/optimize', request, {
    timeout: 120000  // 120秒超时
  });
  return response.data;
};
```

### Epic 005补充（2025-11-04）
- Backend超时从30秒延长至60秒（Story 5.2）
- Frontend超时从360秒优化至120秒（Story 5.3）
- VRP计算时间优化至10-60秒（Story 5.2）

---

## 验证结果

**Story 002验证 (2025-11-02):**
- ✅ 20配送先，3台车辆，计算时间10-20秒
- ✅ Frontend正常显示结果
- ✅ 超时处理正常（模拟测试）

**Epic 005验证 (2025-11-04):**
- ✅ 30配送先，5台车辆，计算时间10-60秒
- ✅ Multi-Depot VRP正常完成
- ✅ 无超时问题（60秒内完成）

---

## 参考资料

- **Story 002文档:** `docs/stories/story-002-optimization-engine.md`
- **Epic 005文档:** `docs/stories/epic-005-demo-data-expansion.md`
- **技术决策分析:** `docs/history/decision-story002-api-algorithm.md`
- **FastAPI异步文档:** https://fastapi.tiangolo.com/async/

---

**文档状态:** ✅ Epic 005完成后回顾更新
**最终更新:** 2025-11-05
**维护者:** 开发团队
