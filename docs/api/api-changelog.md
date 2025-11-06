# API変更履歴 (API Changelog)

> **プロジェクト:** AI自動配車システムデモプロトタイプ
> **最終更新:** 2025-11-05

---

## v1.1.0 - Epic 005 (2025-11-04)

### 🆕 新機能

**Multi-Depot VRP対応:**
- デモデータ生成が2拠点対応（東京・さいたま市）
- 配送先30件対応（東京20件 + さいたま市10件）
- 車両5台対応（東京3台 + さいたま市2台）

### 🔄 変更

**POST `/api/v1/seed/demo-data`:**
- レスポンス: `"detail": "拠点: 2件, 車両: 5台, 配送先: 30件"`（旧: 1件, 3台, 20件）
- 生成データに`depot_id`フィールド追加（Delivery model）

**POST `/api/v1/optimization/optimize`:**
- タイムアウト: 60秒（旧: 30秒）
- 制約追加:
  - ✅ 双重容量制約（重量 + 容積）
  - ✅ 拠点制約（各車両は所属拠点の配送先のみ訪問可能）
- 時間窓変更:
  - `morning`: 8:00-13:00（旧: 8:00-12:00、1時間延長）
  - `afternoon`: 12:00-18:00（旧: 13:00-18:00、1時間重複）

**GET `/api/v1/deliveries`:**
- レスポンスに`depot_id`フィールド追加

### 📊 パフォーマンス改善

- VRP計算時間: 平均30秒 → 10-60秒（30配送先対応）
- 初期解策略変更: `PATH_CHEAPEST_ARC` → `PARALLEL_CHEAPEST_INSERTION`

### 🐛 修正

- 配送点の海上配置問題を解消（固定配送点リスト方式採用）
- HTTP超時設定最適化（Frontend: 360秒→120秒）

### 📝 Documentation

- Epic 005完了: `docs/stories/epic-005-demo-data-expansion.md`
- Multi-Depot VRP決策: `docs/architecture/adr/002-multi-depot-vrp.md`

---

## v1.0.0 - Story 002-004 (2025-11-03)

### 🆕 新機能

**VRP最適化エンジン（Story 002）:**
- `POST /api/v1/optimization/optimize` - VRP最適化実行
- OR-Tools CVRPTW実装
- 制約:
  - ✅ 容量制約（重量）
  - ✅ 時間窓制約（morning/afternoon）
- 基線方案（Simple Assignment）との比較機能

**Frontend統合（Story 003）:**
- OpenStreetMapでのルート表示
- 10色の車両ルートカラーリング
- 結果分析UI（概要・ルート一覧・コスト比較）

**Demo展示増強（Story 004）:**
- 選択状態詳細情報表示（Drawer）
- 最適化前後方案対比Tab
- ルート方向矢印可視化

### 📋 API端点

**POST `/api/v1/seed/demo-data`:**
- デモデータ生成（1拠点・3台・20配送先）

**GET `/api/v1/depots`:**
- 拠点リスト取得（ページネーション対応）

**GET `/api/v1/vehicles`:**
- 車両リスト取得（拠点ID・車両タイプでフィルタ可能）

**GET `/api/v1/deliveries`:**
- 配送先リスト取得（時間窓でフィルタ可能）

**POST `/api/v1/optimization/optimize`:**
- VRP最適化実行（タイムアウト: 30秒）

### 📊 パフォーマンス

- 20配送先・3台車辆: 計算時間 10-20秒
- Frontend渲染: 20マーカー + 3ルート（パフォーマンス良好）

### 📝 Documentation

- Story 002完了: `docs/stories/story-002-optimization-engine.md`
- Story 003完了: `docs/stories/story-003-frontend-integration.md`
- Story 004完了: `docs/stories/story-004-demo-enhancement.md`
- ADR 001: `docs/architecture/adr/001-sync-api-design.md`

---

## v0.1.0 - Story 001 (2025-10-30)

### 🆕 初期リリース

**プロジェクト初期化（Story 001）:**
- Monorepo 構造作成
- FastAPI Backend骨格
- React + TypeScript Frontend骨格
- SQLite データベース設定
- デモデータテンプレート

### 📋 基本API端点

**GET `/health`:**
- ヘルスチェック

**GET `/`:**
- API状態確認

### 📝 Documentation

- Story 001完了: `docs/stories/story-001-project-initialization.md`
- README.md初版
- Architecture.md初版

---

## 🔮 今後の予定

### v1.2.0 - Story 006 (予定)

**E2Eテスト実施:**
- pytestテストカバレッジ向上（目標: 80%以上）
- Frontend E2Eテスト（Playwright/Cypress）

**パフォーマンス最適化:**
- 50配送先対応
- VRP計算時間最適化（目標: 60秒以内）

### v2.0.0 - Future Enhancements (構想)

**非同期API:**
- WebSocket実時進捗推送
- Celery任务队列
- 任务取消功能

**3拠点以上対応:**
- N拠点架構験証
- 拠点容量制约

**実時交通情報:**
- Google Maps Distance Matrix API統合
- 動的ルート再計算

---

## 🔄 変更管理ポリシー

### 破壊的変更（Breaking Changes）

**定義:**
- 既存APIレスポンス構造変更
- 既存エンドポイント削除
- 既存パラメータ変更（デフォルト値変更含む）

**告知:**
- 最低1週間前に告知
- README.mdとAPI Guideに明記

### 非破壊的変更（Non-Breaking Changes）

**定義:**
- 新規エンドポイント追加
- 新規オプションパラメータ追加
- レスポンスへの新規フィールド追加

**告知:**
- リリースノートに記載

---

## 📝 Changelog形式

本Changelogは [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) と [Semantic Versioning](https://semver.org/lang/ja/) に準拠します。

**カテゴリ:**
- `🆕 新機能` - 新規機能追加
- `🔄 変更` - 既存機能変更
- `🐛 修正` - バグ修正
- `📊 パフォーマンス改善` - 性能最適化
- `⚠️ 非推奨` - 将来削除予定機能
- `❌ 削除` - 削除された機能
- `📝 Documentation` - ドキュメント変更

---

**📅 Changelog維持者:** 開発チーム
**🔄 更新頻度:** 各Story/Epic完了後
**📊 最終更新:** 2025-11-05 (Epic 005完了後)
