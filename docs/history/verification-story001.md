# Story 001 验证清单

**验证日期：** 2025-10-30
**验证目的：** 确保基础设施正确，为Story 002做准备
**预计时间：** 30分钟

---

## ✅ 验证清单

### 第1步：后端 - Python 3.11虚拟环境验证 ⭐ 最重要

**状态：** ⏳ 进行中

**执行命令：**
```bash
cd backend

# 1. 检查系统Python版本（任意版本都可以）
python --version
# 或 Windows:
py --version

# 2. 创建Python 3.11虚拟环境
# Windows:
py -3.11 -m venv venv

# macOS/Linux:
# python3.11 -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate

# macOS/Linux:
# source venv/bin/activate

# 4. 验证虚拟环境Python版本（必须是3.11.x）
python --version
```

**期望结果：**
- [ ] 虚拟环境创建成功
- [ ] 激活后显示 `(venv)` 前缀
- [ ] `python --version` 显示 `Python 3.11.x`

**如果失败：**
- 错误："py: No Python 3.11 found" → 需要安装Python 3.11
  - Windows: https://www.python.org/downloads/
  - macOS: `brew install python@3.11`
  - Ubuntu: `sudo apt install python3.11 python3.11-venv`

---

### 第2步：后端 - 安装依赖并验证OR-Tools ⭐ 核心

**状态：** ⏳ 待执行

**执行命令：**
```bash
# 确保虚拟环境已激活（看到 (venv) 前缀）

# 1. 更新pip
python -m pip install --upgrade pip

# 2. 安装所有依赖
pip install -r requirements.txt

# 3. 验证OR-Tools安装 ⭐ 关键验证
python -c "import ortools; print('✅ OR-Tools version:', ortools.__version__)"

# 4. 验证FastAPI安装
python -c "import fastapi; print('✅ FastAPI version:', fastapi.__version__)"

# 5. 验证配置加载
python -c "from app.config import settings; print('✅ Config loaded:', settings.APP_NAME)"
```

**期望结果：**
- [ ] pip install无错误
- [ ] OR-Tools导入成功，显示版本 `9.8.3296`
- [ ] FastAPI导入成功
- [ ] 配置加载成功，显示 `AI自動配車システム`

**如果失败：**
- 错误："No matching distribution found for ortools" → Python版本不是3.11
  - 重新检查 `python --version`
  - 如果不是3.11，删除venv重新创建

---

### 第3步：后端 - FastAPI启动验证

**状态：** ⏳ 待执行

**执行命令：**
```bash
# 确保在backend目录，虚拟环境已激活

# 启动FastAPI开发服务器
uvicorn app.main:app --reload
```

**期望结果：**
- [ ] 启动无错误
- [ ] 看到消息：`INFO: Uvicorn running on http://127.0.0.1:8000`
- [ ] 看到消息：`INFO: Application startup complete`

**浏览器验证（保持服务器运行）：**

1. 访问 Swagger UI:
   - 打开浏览器: http://localhost:8000/docs
   - [ ] 看到 "AI自動配車システム API" 标题
   - [ ] 看到2个端点：`GET /` 和 `GET /health`

2. 测试根端点:
   - 点击 `GET /` → "Try it out" → "Execute"
   - [ ] 返回状态码 200
   - [ ] 返回JSON包含 `"message": "AI自動配車システム API"`

3. 测试健康检查:
   - 点击 `GET /health` → "Try it out" → "Execute"
   - [ ] 返回状态码 200
   - [ ] 返回JSON `{"status": "healthy"}`

**或使用curl测试（新终端）：**
```bash
curl http://localhost:8000/
# 期望：{"message":"AI自動配車システム API","version":"1.0.0","status":"running","docs":"/docs"}

curl http://localhost:8000/health
# 期望：{"status":"healthy"}
```

**验证完成后：**
- 按 `Ctrl+C` 停止服务器

---

### 第4步：前端 - 依赖安装验证

**状态：** ⏳ 待执行

**执行命令：**
```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 验证TypeScript编译
npx tsc --noEmit

# 3. 验证ESLint配置
npm run lint
```

**期望结果：**
- [ ] `npm install` 成功，无错误
- [ ] `npx tsc --noEmit` 无错误（可能有warning，可以忽略）
- [ ] `npm run lint` 执行成功（可能有warning，可以忽略）

**如果失败：**
- 错误："Cannot find module '@types/node'" → 检查package.json是否包含 `@types/node`
- 错误：".eslintrc.cjs not found" → 检查是否有ESLint配置文件

---

### 第5步：前端 - Vite启动验证

**状态：** ⏳ 待执行

**执行命令：**
```bash
# 确保在frontend目录

# 启动Vite开发服务器
npm run dev
```

**期望结果：**
- [ ] 启动无错误
- [ ] 看到消息：`VITE v5.0.11  ready in xxx ms`
- [ ] 看到消息：`Local: http://localhost:5173/`

**浏览器验证：**
1. 访问: http://localhost:5173
2. [ ] 看到页面标题 "🚛 AI自動配車システム"
3. [ ] 看到文本 "デモプロトタイプ - フロントエンド起動成功！"
4. [ ] 页面显示 "バージョン: 1.0.0"
5. [ ] 页面使用Ant Design样式（日文UI）

**验证完成后：**
- 按 `Ctrl+C` 停止服务器

---

### 第6步：前端 - @shared类型导入验证 ⭐ 重要

**状态：** ⏳ 待执行

**创建临时测试文件：**
```bash
# 确保在frontend目录
```

创建文件 `frontend/src/test-import.ts`:

```typescript
// 测试@shared别名是否工作
import { Vehicle, Depot, Delivery, OptimizationRequest } from '@shared/types'

const testVehicle: Vehicle = {
  id: 'test-1',
  vehicle_type: '2t',
  capacity_weight: 2000,
  capacity_volume: 10.0,
  depot_id: 'depot-1',
  available_hours: {
    start_time: '08:00',
    end_time: '18:00'
  },
  cost_per_km: 50,
  cost_per_hour: 3000
}

const testDepot: Depot = {
  id: 'depot-1',
  name: '東京物流センター',
  latitude: 35.6812,
  longitude: 139.7671,
  address: '東京都千代田区',
  operating_hours: {
    start_time: '08:00',
    end_time: '20:00'
  }
}

console.log('✅ Import test passed')
console.log('Vehicle:', testVehicle.id)
console.log('Depot:', testDepot.name)
```

**执行测试：**
```bash
# 验证TypeScript编译
npx tsc src/test-import.ts --noEmit

# 期望：无错误输出
```

**期望结果：**
- [ ] TypeScript编译通过，无错误
- [ ] 说明 `@shared` 别名工作正常

**清理测试文件：**
```bash
# 删除测试文件
rm src/test-import.ts

# Windows:
# del src\test-import.ts
```

---

### 第7步：演示数据验证

**状态：** ⏳ 待执行

**执行命令：**
```bash
cd backend/data/demo_data

# Windows:
type depots.csv
type vehicles.csv
dir

# macOS/Linux:
cat depots.csv
cat vehicles.csv
ls -lh
```

**期望结果：**
- [ ] `depots.csv` 存在，包含4行数据（+1行header）
- [ ] `vehicles.csv` 存在，包含10行数据（+1行header）
- [ ] `deliveries.csv` 存在，包含100行数据（+1行header）
- [ ] CSV格式正确（有header，逗号分隔）

---

## 📊 验证结果汇总

### 后端验证

- [ ] Python 3.11虚拟环境创建成功
- [ ] 虚拟环境Python版本正确（3.11.x）
- [ ] pip install成功，所有依赖安装无错误
- [ ] OR-Tools导入成功（版本：9.8.3296）
- [ ] FastAPI导入成功
- [ ] 配置加载成功
- [ ] FastAPI启动成功
- [ ] Swagger UI可访问（http://localhost:8000/docs）
- [ ] API端点测试通过（/ 和 /health）

### 前端验证

- [ ] npm install成功
- [ ] TypeScript编译通过（无错误）
- [ ] ESLint检查通过
- [ ] Vite启动成功
- [ ] 应用可访问（http://localhost:5173）
- [ ] 欢迎页面显示正确
- [ ] @shared别名工作正常（类型导入测试通过）

### 数据验证

- [ ] 3个CSV文件都存在
- [ ] CSV文件格式正确
- [ ] 数据内容合理

---

## 🚨 问题记录

**遇到的问题：**

1. 问题描述：
   - 错误信息：
   - 解决方法：

2. 问题描述：
   - 错误信息：
   - 解决方法：

（如无问题，写"无问题"）

---

## ✅ 最终结论

**验证结果：**
- [ ] ✅ 全部通过 - 可以开始Story 002
- [ ] ⚠️ 部分问题已修复 - 可以开始Story 002
- [ ] ❌ 有严重问题 - 需要修复后重新验证

**签名：** ___________
**日期：** 2025-10-30
**时间：** ___________

---

## 📝 备注

（记录其他需要注意的事项）

---

**下一步：** 如果验证通过 → 创建 `docs/stories/story-002-optimization-engine.md`
