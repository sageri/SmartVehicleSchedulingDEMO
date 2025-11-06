# AI自動配車システム - 文档导航

> **最终更新:** 2025-11-05
> **项目状态:** ✅ Epic 005 完了（Production Demo Ready）

---

## 📖 文档概览

本文档集提供AI自動配車システムデモプロトタイプ的完整技术文档，涵盖架构设计、API规格、开发指南、部署流程以及开发历史。

---

## 🗂️ 文档结构

```
docs/
├── README.md (本文档)           # 📘 文档导航索引
├── brownfield-architecture.md   # 🏗️ Brownfield架构文档（真实状态记录）
│
├── architecture/                # 🏛️ 架构设计
│   ├── architecture.md          # 全栈架构文档（Epic 005已更新）
│   ├── front-end-spec.md        # UI/UX仕様書
│   └── adr/                     # Architecture Decision Records
│       ├── 001-sync-api-design.md     # 同步API设计决策
│       └── 002-multi-depot-vrp.md     # Multi-Depot VRP决策
│
├── api/                         # 📡 API文档
│   ├── api-guide.md             # API使用指南（从backend迁移）
│   └── api-changelog.md         # API版本变更记录
│
├── development/                 # 💻 开发指南
│   ├── setup-guide.md           # 环境搭建详细步骤
│   ├── troubleshooting.md       # 故障排查手册
│   └── verification-checklist.md  # 验证清单（从根目录迁移）
│
├── stories/                     # 📝 开发故事
│   ├── epic-005-demo-data-expansion.md  # Epic 005主文档
│   ├── story-5.*.md             # Epic 005相关Story
│   └── story-001~004-*.md       # 历史Story（保留原位置）
│
└── history/                     # 📦 历史文档归档
    ├── verification-story001.md
    ├── decision-story002-api-algorithm.md
    └── ... (过程文档)
```

---

## 🚀 快速开始

### 新成员入门路径

1. **📘 项目概览** → [根目录README.md](../README.md)
   - 了解项目目标、技术栈、快速启动

2. **🏗️ 架构理解** → [architecture.md](architecture/architecture.md)
   - 全栈架构设计、技术选型、模块划分

3. **💻 环境搭建** → [setup-guide.md](development/setup-guide.md)
   - Python 3.11虚拟环境、OR-Tools安装、数据库初始化

4. **📡 API使用** → [api-guide.md](api/api-guide.md) | [Backend API Guide](../backend/docs/API_GUIDE.md)
   - API端点、请求示例、错误处理

5. **🎨 前端开发** → [frontend README](../frontend/README.md)
   - React组件、Leaflet地图、状态管理

---

## 📚 按用途查找文档

### 🏗️ 架构与设计

| 文档 | 用途 | 适用对象 |
|------|------|---------|
| [architecture.md](architecture/architecture.md) | 全栈架构设计、Epic 005最新状态 | 全员 |
| [brownfield-architecture.md](brownfield-architecture.md) | 真实状态记录（技术债务、约束） | AI Agent、新成员 |
| [front-end-spec.md](architecture/front-end-spec.md) | UI/UX详细规格、组件设计 | 前端开发者 |
| [ADR 001](architecture/adr/001-sync-api-design.md) | 同步API设计决策记录 | 后端开发者 |
| [ADR 002](architecture/adr/002-multi-depot-vrp.md) | Multi-Depot VRP技术决策 | 算法工程师 |

### 📡 API文档

| 文档 | 用途 | 适用对象 |
|------|------|---------|
| [api-guide.md](api/api-guide.md) | API端点使用指南（Epic 005最新） | 全员 |
| [api-changelog.md](api/api-changelog.md) | API版本变更历史 | API用户 |
| [Swagger UI](http://localhost:8000/docs) | 交互式API文档（需启动Backend） | 开发测试 |

### 💻 开发指南

| 文档 | 用途 | 适用对象 |
|------|------|---------|
| [setup-guide.md](development/setup-guide.md) | 环境搭建详细步骤 | 新成员 |
| [troubleshooting.md](development/troubleshooting.md) | 常见问题FAQ | 全员 |
| [verification-checklist.md](development/verification-checklist.md) | 验证清单 | 开发者 |
| [根目录AGENTS.md](../AGENTS.md) | AI Agent开发规范（含Epic 005实践总结） | AI Agent |

### 📝 开发历史

| 文档 | 用途 | 适用对象 |
|------|------|---------|
| [epic-005-demo-data-expansion.md](stories/epic-005-demo-data-expansion.md) | Epic 005完整文档（Multi-Depot VRP） | 全员 |
| [story-5.*.md](stories/) | Epic 005各Story详细文档 | 开发者 |
| [story-001~004.md](stories/) | 历史Story文档 | 参考 |
| [history/](history/) | 过程文档归档（验证、决策分析） | 参考 |

---

## 🎯 按任务场景查找

### 场景1: 我想了解系统架构
1. 阅读 [architecture.md](architecture/architecture.md) - 全栈架构概览
2. 阅读 [epic-005-demo-data-expansion.md](stories/epic-005-demo-data-expansion.md) - 最新实现状态
3. 参考 [brownfield-architecture.md](brownfield-architecture.md) - 真实约束和技术债务

### 场景2: 我想开始开发
1. 阅读 [setup-guide.md](development/setup-guide.md) - 环境搭建
2. 阅读 [根目录README.md](../README.md) - 快速启动命令
3. 参考 [AGENTS.md](../AGENTS.md) - 开发规范（含Epic 005实践）

### 场景3: 我想调用API
1. 阅读 [api-guide.md](api/api-guide.md) - API端点使用指南
2. 访问 [Swagger UI](http://localhost:8000/docs) - 交互式测试
3. 参考 [api-changelog.md](api/api-changelog.md) - 版本变更历史

### 场景4: 我遇到了问题
1. 查阅 [troubleshooting.md](development/troubleshooting.md) - 常见问题FAQ
2. 检查 [epic-005-demo-data-expansion.md](stories/epic-005-demo-data-expansion.md) - Risk Mitigation章节
3. 参考 [brownfield-architecture.md](brownfield-architecture.md) - Known Issues章节

### 场景5: 我想了解技术决策背景
1. 阅读 [ADR文档](architecture/adr/) - 架构决策记录
2. 参考 [epic-005主文档](stories/epic-005-demo-data-expansion.md) - 完整决策过程
3. 查看 [AGENTS.md § 14](../AGENTS.md#14-epic-005-实践总结) - Epic 005实践总结

---

## 📊 文档类型说明

### 核心文档（必读）
- ✅ 始终保持最新
- 🔒 修改需经过Review
- 📍 位于docs根目录或architecture/

### 参考文档（按需查阅）
- 📚 提供详细信息
- 🔄 定期更新
- 📁 位于api/、development/目录

### 历史文档（存档）
- 📦 记录开发过程
- 🗄️ 不再主动维护
- 📂 位于stories/、history/目录

---

## 🔧 文档维护规范

### 新建文档时
1. 确定文档类型（核心/参考/历史）
2. 放置在正确目录
3. 更新本导航文档
4. 添加文档元信息（作者、日期、状态）

### 更新文档时
1. 更新文档内的"最终更新"日期
2. 重大变更需添加Change Log
3. 影响其他文档时需同步更新
4. 过时文档移至history/归档

### 文档归档时
1. 评估文档是否仍有参考价值
2. 有价值→移至history/
3. 无价值→删除（需Git记录）
4. 更新本导航文档

---

## 📞 文档反馈

发现文档问题或有改进建议？

- **缺失文档:** 在项目Issue中提出需求
- **内容错误:** 提交PR修正
- **结构建议:** 联系项目维护者

---

## 📅 文档更新历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2025-11-05 | 1.0 | 初始版本（文档导航索引创建） | Claude |

---

**🤖 文档生成工具:** Claude Code AI Agent
**📊 文档状态:** ✅ Epic 005完成后首次发布
**🔄 维护周期:** 每个Epic完成后更新
