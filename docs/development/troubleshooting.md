# 故障排查手册（Troubleshooting Guide）

> **目标:** 快速诊断和解决常见问题
> **最终更新:** 2025-11-05
> **适用版本:** Epic 005 (v1.1.0)

---

## 📋 快速诊断流程

### 问题分类决策树

```
问题发生 →
├─ Backend无法启动？ → §1 Backend问题
├─ Frontend无法启动？ → §2 Frontend问题
├─ VRP计算失败？ → §3 VRP优化问题
├─ 数据生成失败？ → §4 数据生成问题
├─ 地图显示异常？ → §5 地图可视化问题
└─ 其他问题 → §6 其他常见问题
```

---

## §1 Backend问题

### 1.1 Backend无法启动 - ModuleNotFoundError

**症状:**
```
ModuleNotFoundError: No module named 'ortools'
ModuleNotFoundError: No module named 'fastapi'
```

**原因:** 虚拟环境未激活或依赖未安装

**解决步骤:**
```bash
cd backend

# Step 1: 激活虚拟环境
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux

# Step 2: 确认Python版本（必须3.11.x）
python --version

# Step 3: 重新安装依赖
pip install -r requirements.txt

# Step 4: 启动Backend
uvicorn app.main:app --reload
```

---

### 1.2 OR-Tools安装失败

**症状:**
```
ERROR: Could not find a version that satisfies the requirement ortools==9.8.3296
ERROR: No matching distribution found for ortools
```

**原因:** Python版本不是3.11

**诊断:**
```bash
python --version
# 如果不是"Python 3.11.x"，说明虚拟环境创建错误
```

**解决:**
```bash
cd backend

# Step 1: 删除错误的虚拟环境
rm -rf venv            # macOS/Linux
rmdir /s venv          # Windows

# Step 2: 使用Python 3.11创建虚拟环境
py -3.11 -m venv venv  # Windows
python3.11 -m venv venv  # macOS/Linux

# Step 3: 激活并验证
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS/Linux
python --version         # 必须显示3.11.x

# Step 4: 安装依赖
pip install -r requirements.txt
```

---

### 1.3 Database is locked

**症状:**
```
sqlite3.OperationalError: database is locked
```

**原因:** SQLite被多个Backend进程同时访问

**解决:**
```bash
# Step 1: 停止所有Backend进程
# Windows: 任务管理器 → 结束所有python.exe/uvicorn.exe
# macOS/Linux: pkill -f uvicorn

# Step 2: 删除锁文件
rm backend/data/demo.db-journal  # 如果存在

# Step 3: 重启Backend
cd backend
uvicorn app.main:app --reload

# 预防措施: 使用单个Backend实例，避免--workers参数
```

---

### 1.4 CORS错误

**症状:** Frontend Console显示
```
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/...'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**原因:** Backend CORS配置未包含Frontend地址

**解决:**
```python
# backend/app/config.py
class Settings(BaseSettings):
    CORS_ORIGINS: list = ["http://localhost:5173"]  # 确认存在
```

**验证:**
```bash
# 重启Backend后测试
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8000/api/v1/seed/demo-data
```

---

## §2 Frontend问题

### 2.1 Frontend无法启动 - 端口占用

**症状:**
```
Error: listen EADDRINUSE: address already in use :::5173
```

**原因:** 5173端口被占用

**解决:**
```bash
# 方法1: 查找并结束占用进程
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5173
kill -9 <PID>

# 方法2: 使用其他端口
npm run dev -- --port 5174
```

---

### 2.2 node_modules损坏

**症状:**
```
Error: Cannot find module 'react'
Module not found: Can't resolve 'antd'
```

**解决:**
```bash
cd frontend

# Step 1: 删除node_modules和lock文件
rm -rf node_modules package-lock.json  # macOS/Linux
rmdir /s node_modules && del package-lock.json  # Windows

# Step 2: 清理npm缓存
npm cache clean --force

# Step 3: 重新安装
npm install

# Step 4: 启动
npm run dev
```

---

### 2.3 Frontend无法连接Backend

**症状:** 页面显示"ネットワークエラー: サーバーに接続できません"

**诊断清单:**
```bash
# 1. Backend是否运行？
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# 2. Frontend端口是否正确？
# 检查浏览器地址栏是否为 http://localhost:5173

# 3. API Base URL是否正确？
# 检查 frontend/src/services/api.ts
# baseURL应为 'http://localhost:8000'

# 4. 网络代理问题？
# 关闭VPN/代理重试
```

**解决:**
```bash
# 完整重启流程
# Terminal 1: Backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# 验证
curl http://localhost:8000/health
curl http://localhost:5173  # 应返回HTML
```

---

## §3 VRP优化问题

### 3.1 VRP计算超时（60秒）

**症状:** Frontend显示"最適化に失敗しました: タイムアウト"

**原因分析:**
1. 配送先数过多（>50件）
2. 时间窗制约过严（指定なし比率低）
3. 拠点制约导致无解

**解决方案:**

**临时缓解:**
```bash
# 减少配送先数
# 修改 backend/app/api/v1/seed.py
DELIVERIES_PER_DEPOT = {
    "depot-tokyo": 15,     # 从20减至15
    "depot-saitama": 8,    # 从10减至8
}

# 提升时间窗柔性
TIME_WINDOW_WEIGHTS = [0.1, 0.2, 0.7]  # 指定なし提升至70%
```

**长期优化:**
```python
# backend/app/services/vrp_service.py
# 延长超时时间（谨慎使用）
search_parameters.time_limit.seconds = 120  # 从60秒延长至120秒

# 调整初期解策略
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC  # 自动选择
)
```

---

### 3.2 VRP无解（unassigned_deliveries非空）

**症状:** API返回`"unassigned_deliveries": ["delivery-001", ...]`

**原因:**
1. 車両容量不足
2. 时间窗制约冲突
3. 拠点制约导致无法分配

**诊断:**
```bash
# 检查日志
# Backend终端会显示:
# WARNING: X deliveries could not be assigned
```

**解决:**
```python
# 方案1: 增加車両数量
VEHICLE_ALLOCATION = {
    "depot-tokyo": {
        "2t": ["vehicle-101", "vehicle-102", "vehicle-105"],  # 增加1台
        "4t": ["vehicle-201"],
    },
    # ...
}

# 方案2: 放宽时间窗
TIME_WINDOW_WEIGHTS = [0.1, 0.1, 0.8]  # 80%指定なし

# 方案3: 检查拠点制约
# 确认所有配送先的depot_id与车辆depot_id匹配
```

---

### 3.3 基线方案（Baseline）异常

**症状:** `baseline_metrics`全为0或异常大

**原因:** Simple Assignment算法失败

**解决:**
```python
# backend/app/services/baseline_service.py
# 检查日志输出
logger.info(f"Baseline: {len(assigned)} assigned, {len(unassigned)} unassigned")

# 如果unassigned过多，检查容量设置
```

---

## §4 数据生成问题

### 4.1 配送点落海问题（已在Epic 005解决）

**症状:** 地图上部分配送先显示在海上

**Epic 005解决方案:** 固定配送点列表

**如果仍出现（不应该）:**
```bash
# 检查是否使用了旧代码
grep -n "random_bearing" backend/app/api/v1/seed.py
# 应无输出（已废除随机生成）

# 验证固定配送点列表
grep -A 5 "FIXED_DELIVERY_LOCATIONS" backend/app/api/v1/seed.py
```

---

### 4.2 depot_id关联错误

**症状:** VRP优化时车辆访问错误拠点的配送先

**诊断:**
```bash
# 检查数据库中的depot_id
sqlite3 backend/data/demo.db
SELECT id, customer_name, depot_id FROM deliveries LIMIT 10;

# Expected:
# delivery-001~020 → depot-tokyo
# delivery-021~030 → depot-saitama
```

**解决:**
```bash
# 删除数据库重新生成
rm backend/data/demo.db
python -c "from app.database import init_db; init_db()"
curl -X POST http://localhost:8000/api/v1/seed/demo-data
```

---

## §5 地图可视化问题

### 5.1 地图不显示

**症状:** 地图区域显示为灰色或白色

**原因1: Leaflet CSS未加载**
```html
<!-- frontend/index.html应包含 -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

**原因2: 网络无法访问OSM Tile服务器**
```bash
# 测试OSM Tile可访问性
curl -I https://tile.openstreetmap.org/0/0/0.png
# Expected: HTTP/1.1 200 OK
```

**解决:**
```bash
# 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete → 清除缓存图像

# 检查Frontend Console错误
# F12 → Console Tab → 查找tile加载错误
```

---

### 5.2 マーカー不显示

**症状:** 地图正常但没有拠点/配送先マーカー

**诊断:**
```javascript
// Frontend Console执行
console.log(demoStore.getState().depots);  // 应有2个拠点
console.log(demoStore.getState().deliveries);  // 应有30个配送先
```

**解决:**
```bash
# 确认数据已生成
curl http://localhost:8000/api/v1/depots | jq '.total'
# Expected: 2

curl http://localhost:8000/api/v1/deliveries | jq '.total'
# Expected: 30

# 如果为0，重新生成数据
curl -X POST http://localhost:8000/api/v1/seed/demo-data
```

---

### 5.3 ルート线不显示

**症状:** 优化完成但地图上无路径

**诊断:**
```javascript
// Frontend Console执行
console.log(demoStore.getState().optimizationResult);
// 应有routes数组，每个route有stops数组
```

**解决:**
```bash
# 确认API返回正确
curl -X POST http://localhost:8000/api/v1/optimization/optimize \
  -H "Content-Type: application/json" \
  -d '{"depot_ids":["depot-tokyo"],"vehicle_ids":["vehicle-101"],"delivery_ids":["delivery-001","delivery-002"]}' \
  | jq '.routes | length'
# Expected: >0
```

---

## §6 其他常见问题

### 6.1 Hot Reload不工作

**Backend (uvicorn):**
```bash
# 确认使用--reload参数
uvicorn app.main:app --reload

# 如果仍不工作，手动重启
# Ctrl+C → 重新运行uvicorn命令
```

**Frontend (Vite):**
```bash
# 确认vite.config.ts有HMR配置
# 如果不工作，重启npm run dev
```

---

### 6.2 端口冲突

**症状:** Backend/Frontend启动失败，提示端口占用

**全局解决方案:**
```bash
# 查找占用端口的进程
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# macOS/Linux
lsof -i :8000
lsof -i :5173

# 结束进程
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>
```

---

### 6.3 Git操作失败

**症状:** `git commit`或`git push`失败

**常见原因:**
```bash
# 1. 未配置Git用户
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 2. 大文件未gitignore
# 检查.gitignore包含:
# backend/data/*.db
# node_modules/
# venv/

# 3. 分支冲突
git status  # 查看冲突文件
# 手动解决冲突后
git add .
git commit -m "解决冲突"
```

---

## 🔍 高级诊断工具

### Backend日志分析

```bash
# 启用DEBUG模式
# backend/app/config.py
DEBUG = True

# 查看详细SQL日志
SQLALCHEMY_ECHO = True

# 重启Backend查看详细日志
```

### Frontend性能分析

```javascript
// 浏览器Console执行
performance.mark('start');
// 执行操作（如VRP优化）
performance.mark('end');
performance.measure('operation', 'start', 'end');
console.table(performance.getEntriesByType('measure'));
```

---

## 📞 获取更多帮助

如果以上方法无法解决问题：

1. **查阅相关文档:**
   - [Epic 005文档](../stories/epic-005-demo-data-expansion.md) - Risk Mitigation章节
   - [Brownfield架构文档](../brownfield-architecture.md) - Known Issues章节
   - [环境搭建指南](setup-guide.md) - 详细安装步骤

2. **检查GitHub Issues:**
   - 搜索类似问题
   - 提交新Issue（附上错误日志）

3. **联系维护者:**
   - 提供完整错误信息
   - 说明复现步骤
   - 附上环境信息（Python版本、Node版本、OS）

---

**📅 最终更新:** 2025-11-05
**✅ 验证状态:** Epic 005环境验证通过
**👤 维护者:** 开发团队
**🔄 维护周期:** 每个Epic完成后更新
