# AI自動配車システム - Frontend 使用ガイド

## 📋 概要

React + TypeScript + Ant Design による AI 配車システムの Frontend 実装。
Backend API (FastAPI) と連携し、VRP 最適化結果を地図上で可視化します。

---

## 🚀 クイックスタート

### 1. 依存インストール

```bash
cd frontend
npm install
```

### 2. Backend 起動（前提条件）

別ターミナルで Backend API を起動：

```bash
cd backend
uvicorn app.main:app --reload
```

**確認:** http://localhost:8000/docs で Swagger UI が開けることを確認

### 3. Frontend 起動

```bash
cd frontend
npm run dev
```

**アクセス:** http://localhost:5173

---

## 🎯 使用方法

### Step 1: デモデータ作成 (Epic 005対応)

1. 左サイドバーの「デモデータ作成」ボタンをクリック
2. 拠点2件（東京・さいたま市）、車両5台、配送先30件が自動生成される
3. 地図上に2拠点（青）と配送先30件（赤/オレンジ/緑）が表示される

### Step 2: VRP 最適化実行

1. 左サイドバーの「VRP最適化実行」ボタンをクリック
2. 計算中（2-30秒）は Loading 表示
3. 完了すると地図上にルートが色分けして表示される

### Step 3: 結果確認

**📊 概要タブ:**
- 距離削減率、コスト削減率、積載率改善、計算時間

**🚛 ルート一覧タブ:**
- 各ルートの詳細情報（距離、時間、コスト、積載率）
- 行クリックで地図上でハイライト

**📈 コスト比較タブ:**
- 基線（simple_assignment）vs 最適化後の比較チャート

---

## 📁 フォルダ構成

```
frontend/src/
├── components/
│   ├── Layout/
│   │   └── AppLayout.tsx          # メインレイアウト
│   ├── Control/
│   │   └── ControlPanel.tsx       # 操作パネル
│   ├── Map/
│   │   ├── MapView.tsx             # 地図コンポーネント
│   │   ├── DepotMarker.tsx         # 拠点マーカー
│   │   ├── DeliveryMarker.tsx      # 配送先マーカー
│   │   └── RoutePolyline.tsx       # ルート線
│   └── Result/
│       └── ResultPanel.tsx         # 結果表示パネル
├── services/
│   └── api.ts                      # API Client (Axios)
├── stores/
│   └── useVRPStore.ts              # Zustand Store
├── types/
│   └── index.ts                    # TypeScript 型定義
├── App.tsx                         # ルートコンポーネント
└── main.tsx                        # エントリーポイント
```

---

## 🧪 動作確認チェックリスト

### ✅ 基本動作

- [ ] Frontend が http://localhost:5173 で起動する
- [ ] Backend API が http://localhost:8000 で起動している
- [ ] 「デモデータ作成」ボタンで 2拠点・30配送先が生成される (Epic 005)
- [ ] 地図上に拠点と配送先マーカーが表示される

### ✅ VRP 最適化

- [ ] 「VRP最適化実行」ボタンをクリックできる
- [ ] Loading 表示が出る（2-30秒）
- [ ] 最適化完了後、地図上にルートが表示される
- [ ] ルート線が色分けされている

### ✅ 結果表示

- [ ] 「📊 概要」タブに改善指標が表示される
- [ ] 「🚛 ルート一覧」タブにテーブルが表示される
- [ ] 「📈 コスト比較」タブにチャートが表示される
- [ ] ルート線をクリックすると詳細ポップアップが表示される

---

## 🔧 トラブルシューティング

### 問題1: Backend に接続できない

**エラー:** `ネットワークエラー: サーバーに接続できません`

**解決方法:**
1. Backend が起動しているか確認: `http://localhost:8000/docs`
2. `.env` ファイルの `VITE_API_BASE_URL` を確認
3. CORS 設定を確認（Backend `app/main.py` の `allow_origins`）

### 問題2: 地図が表示されない

**解決方法:**
1. Leaflet CSS が読み込まれているか確認
2. ブラウザのコンソールでエラーを確認
3. `npm install leaflet react-leaflet @types/leaflet` を再実行

### 問題3: マーカーアイコンが表示されない

**解決方法:**
MapView.tsx の Leaflet default icon 設定を確認（Vite 環境での既知問題）

---

## 🛠 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# 型チェック
npm run build

# Lint チェック
npm run lint

# テスト実行
npm run test
```

---

## 📊 使用技術

| Technology | Version | 用途 |
|------------|---------|------|
| React | 18.2+ | UI Framework |
| TypeScript | 5.3+ | 型安全 |
| Ant Design | 5.12+ | UI Components |
| Leaflet | 1.9+ | 地図表示 |
| React-Leaflet | 4.2+ | React ラッパー |
| Zustand | 4.4+ | 状態管理 |
| Axios | 1.6+ | HTTP Client |
| Recharts | 2.10+ | グラフ表示 |
| Vite | 5.0+ | ビルドツール |

---

## 🎨 UI 設計

### レイアウト

- **Header:** タイトル（AI自動配車システム - Demo）
- **Sider:** 操作パネル（幅360px）
  - デモデータ作成ボタン
  - 選択状態サマリー
  - VRP最適化実行ボタン
- **Content:** 地図 + 結果表示

### 色設計

- **拠点:** 青 (#1890ff)
- **配送先（morning）:** 赤 (#ff4d4f)
- **配送先（afternoon）:** オレンジ (#ff7a45)
- **配送先（anytime）:** 緑 (#52c41a)
- **ルート:** 10色ローテーション（#1f77b4, #ff7f0e, ...）

---

## 📝 既知の制限

1. ~~**単一拠点のみ**~~ → ✅ **Epic 005で解決:** Multi-Depot対応完了（2拠点）
2. **同期 API:** 最適化実行中は他の操作不可（60秒上限、Epic 005で延長）
3. **オフライン地図非対応:** インターネット接続必要（OpenStreetMap）

---

## 🚀 次のステップ

Epic 005 完了後の拡張案：

1. **リアルタイム進捗表示:** WebSocket で計算進捗を表示
2. **ルートアニメーション:** 車両が動くアニメーション
3. **カスタムデータ入力:** CSV アップロード機能
4. ~~**複数拠点対応**~~ → ✅ Epic 005で実装完了（2拠点対応）
5. **3拠点以上への拡張:** 拠点数の段階的拡大
6. **レスポンシブ対応:** モバイル表示最適化

---

**作成者:** 開発チーム
**最終更新:** 2025-11-05
**Status:** ✅ Epic 005 実装完了 (Multi-Depot VRP対応)
