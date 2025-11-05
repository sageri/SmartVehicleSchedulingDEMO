# 环境搭建详细指南

> **目标:** 帮助新成员快速搭建AI自動配車システム开发环境
> **最终更新:** 2025-11-05

---

## 📋 系统需求

### 必需软件

| 软件 | 版本 | 用途 | 下载链接 |
|------|------|------|---------|
| **Python** | **3.11.x** | Backend运行时（强制要求） | https://www.python.org/downloads/ |
| Node.js | 18.x+ | Frontend构建 | https://nodejs.org/ |
| Git | 2.x+ | 版本控制 | https://git-scm.com/ |

### 可选软件

| 软件 | 版本 | 用途 |
|------|------|------|
| VS Code | 最新版 | 推荐IDE |
| Python 3.14 | 最新版 | 开发环境（非运行时） |
| 7-Zip | 最新版 | 压缩文件解压 |

---

## ⚠️ 关键约束

### Python版本约束（重要！）

**Backend运行时必须使用Python 3.11：**
- ❌ **Python 3.12/3.14不支持** - OR-Tools 9.8不兼容
- ✅ 开发环境可使用任意版本（如3.14）
- ✅ Backend运行时强制使用3.11虚拟环境

**验证方法：**
```bash
# 检查系统Python版本
py --version          # Windows
python3 --version     # macOS/Linux

# 检查是否已安装Python 3.11
py -3.11 --version    # Windows
python3.11 --version  # macOS/Linux
```

---

## 🚀 快速搭建步骤

### Step 1: 克隆项目

```bash
git clone <repository-url>
cd VBA
```

### Step 2: Backend环境搭建（Python 3.11虚拟环境）

#### 2.1 安装Python 3.11（如未安装）

**Windows:**
1. 访问 https://www.python.org/downloads/
2. 下载Python 3.11.x（最新3.11版本）
3. 安装时勾选"Add Python 3.11 to PATH"
4. 验证: `py -3.11 --version`

**macOS:**
```bash
brew install python@3.11
python3.11 --version
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
python3.11 --version
```

#### 2.2 创建Python 3.11虚拟环境

```bash
cd backend

# Windows
py -3.11 -m venv venv
venv\Scripts\activate

# macOS/Linux
python3.11 -m venv venv
source venv/bin/activate

# 验证虚拟环境Python版本（必须是3.11.x）
python --version
```

**Expected Output:**
```
Python 3.11.x
```

#### 2.3 安装Backend依赖

```bash
# 确保虚拟环境已激活（提示符前有(venv)）
pip install --upgrade pip
pip install -r requirements.txt
```

**常见问题：**
- **OR-Tools安装失败** → 确认Python版本是3.11.x
- **权限错误** → Windows用`pip install --user`
- **网络超时** → 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

#### 2.4 初始化数据库

```bash
# 虚拟环境激活状态下
python -c "from app.database import init_db; init_db()"
```

**预期结果：**
- 创建`backend/data/demo.db`文件
- 无错误信息

#### 2.5 启动Backend

```bash
uvicorn app.main:app --reload
```

**验证：**
- 访问 http://localhost:8000
- 访问 http://localhost:8000/docs（Swagger UI）

---

### Step 3: Frontend环境搭建

#### 3.1 安装Node.js（如未安装）

**验证：**
```bash
node --version    # 需要 v18.0.0+
npm --version
```

**安装（如需要）:**
- Windows/macOS: https://nodejs.org/ 下载LTS版
- Ubuntu: `sudo apt install nodejs npm`

#### 3.2 安装Frontend依赖

```bash
cd frontend
npm install
```

**常见问题：**
- **node_modules损坏** → `rm -rf node_modules && npm install`
- **网络超时** → 使用淘宝镜像: `npm install --registry=https://registry.npmmirror.com`

#### 3.3 启动Frontend

```bash
npm run dev
```

**验证：**
- 访问 http://localhost:5173
- 看到"AI自動配車システム - Demo"界面

---

### Step 4: 生成演示数据

**方法1: Frontend UI**
1. 访问 http://localhost:5173
2. 点击"デモデータ作成"按钮
3. 等待3秒，地图上显示2拠点+30配送先

**方法2: cURL**
```bash
curl -X POST http://localhost:8000/api/v1/seed/demo-data
```

**预期结果:**
```json
{
  "message": "デモデータを作成しました",
  "detail": "拠点: 2件, 車両: 5台, 配送先: 30件"
}
```

---

## 🧪 验证安装

### 完整验证清单

运行以下命令验证环境：

```bash
# Backend验证
cd backend
python --version           # 必须 3.11.x
python -m py_compile app/main.py  # 语法检查
curl http://localhost:8000/health  # API响应

# Frontend验证
cd frontend
npm run lint              # ESLint检查
npm run build             # 生产构建测试

# 集成验证
curl -X POST http://localhost:8000/api/v1/seed/demo-data
curl http://localhost:8000/api/v1/depots
```

**全部通过后：** ✅ 环境搭建成功！

---

## 🔧 IDE配置（VS Code推荐）

### 安装推荐扩展

**Python开发:**
- Python (Microsoft)
- Pylance
- Python Debugger

**TypeScript/React开发:**
- ESLint
- Prettier - Code formatter
- ES7+ React/Redux/React-Native snippets

### VS Code settings.json（推荐）

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## 🐛 常见问题排查

### 问题1: Backend无法启动 - ModuleNotFoundError

**错误信息:** `ModuleNotFoundError: No module named 'ortools'`

**原因:** 虚拟环境未激活或依赖未安装

**解决:**
```bash
cd backend
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

---

### 问题2: OR-Tools安装失败

**错误信息:** `ERROR: Could not find a version that satisfies the requirement ortools`

**原因:** Python版本不是3.11

**解决:**
```bash
python --version  # 确认是3.11.x

# 如果不是，重新创建虚拟环境
rm -rf venv
py -3.11 -m venv venv  # Windows
python3.11 -m venv venv  # macOS/Linux
```

---

### 问题3: Frontend无法连接Backend

**错误信息:** `Network Error: Cannot connect to server`

**检查清单:**
1. Backend是否运行？ → 访问 http://localhost:8000/docs
2. CORS配置是否正确？ → 检查`backend/app/config.py`中的`CORS_ORIGINS`
3. Frontend端口是否正确？ → 确认运行在5173端口

**解决:**
```bash
# 重启Backend
cd backend
uvicorn app.main:app --reload

# 检查CORS配置
# backend/app/config.py应包含:
CORS_ORIGINS = ["http://localhost:5173"]
```

---

### 问题4: 地图不显示

**原因:** Leaflet CSS未加载或网络问题

**解决:**
1. 检查浏览器Console是否有tile加载错误
2. 确认网络可访问`tile.openstreetmap.org`
3. 清除浏览器缓存重试

---

### 问题5: Database is locked

**错误信息:** `database is locked`

**原因:** SQLite被多个进程访问

**解决:**
```bash
# 停止所有Backend进程
# Windows: Ctrl+C 或任务管理器结束python.exe
# macOS/Linux: pkill -f uvicorn

# 删除锁文件（如果存在）
rm backend/data/demo.db-journal

# 重启Backend
cd backend
uvicorn app.main:app --reload
```

---

## 📚 下一步

环境搭建完成后，建议阅读：

1. [架构文档](../architecture/architecture.md) - 了解系统设计
2. [API指南](../api/api-guide.md) - 学习API使用
3. [AGENTS.md](../../AGENTS.md) - 开发规范（含Epic 005实践）
4. [故障排查手册](troubleshooting.md) - 深入问题解决

---

## 🤝 获取帮助

遇到未列出的问题？

1. 查阅 [故障排查手册](troubleshooting.md)
2. 查看 [Epic 005文档](../stories/epic-005-demo-data-expansion.md) Risk Mitigation章节
3. 提交Issue到项目仓库

---

**📅 最终更新:** 2025-11-05
**✅ 验证状态:** Epic 005环境验证通过
**👤 维护者:** 开发团队
