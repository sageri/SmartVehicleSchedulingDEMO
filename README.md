# AI自動配車システムデモプロトタイプ

**AI Automatic Vehicle Routing System - Demo Prototype**

> **🚧 プロジェクト状態：** Story 003 完了（Frontend統合完了）
> **📅 最終更新：** 2025-11-03
> **✅ 現在の実装：** Backend VRP API、Frontend UI、地図表示、結果分析UI
> **🔜 開発予定：** E2Eテスト、パフォーマンス最適化（Story 004以降）

---

## 📋 プロジェクト概要

日本の物流業界向けのAI自動配車システムのデモンストレーション用プロトタイプ。4つの集荷拠点、100件の配送先、10台の車両を使用した最適化配車のデモンストレーション。

**計画機能（最終デモ目標）：**
- 🚛 車両ルート最適化（VRP - Vehicle Routing Problem）
- 📍 OpenStreetMapベースのビジュアル化
- 📊 コスト削減分析
- ⚡ 高速計算（2-5秒目標）
- 🎯 時間窓制約対応

**現在の実装状態（Story 001完了）：**
- ✅ Monorepo プロジェクト構造
- ✅ FastAPI 基本骨格（ヘルスチェックAPI）
- ✅ React + TypeScript フロントエンド骨格
- ✅ 共有型定義（TypeScript interfaces）
- ✅ デモデータCSVテンプレート
- ✅ 開発環境設定（VSCode、lint、test構成）

---

## 🏗️ 技術スタック

### フロントエンド
- **Framework:** React 18.2+ with TypeScript 5.3+
- **UI Library:** Ant Design 5.12+
- **Map:** Leaflet 1.9+ + OpenStreetMap
- **State:** Zustand 4.4+
- **Build:** Vite 5.0+

### バックエンド
- **Framework:** FastAPI 0.109+
- **Language:** **Python 3.11（厳密）** - 仮想環境必須
  - ⚠️ Python 3.12+/3.14では OR-Tools が動作しません
- **Database:** SQLite 3.40+
- **ORM:** SQLAlchemy 2.0+
- **Optimization:** OR-Tools 9.8+ (Google)

---

## 🚀 クイックスタート

### 前提条件

- **Python 3.11** （プロジェクト実行用 - 仮想環境で使用）
  - 開発環境は任意のPythonバージョン（3.14等）でOK
  - **重要:** バックエンド実行には Python 3.11 の仮想環境が必要
- Node.js 18+
- Git

### インストールと起動

**1. リポジトリのクローン**
```bash
git clone <repository-url>
cd VBA
```

**2. バックエンド起動**

**Python 3.11仮想環境の作成（初回のみ）:**
```bash
cd backend

# Windows
py -3.11 -m venv venv
venv\Scripts\activate

# macOS/Linux
python3.11 -m venv venv
source venv/bin/activate

# 仮想環境のPythonバージョン確認（3.11.xであること）
python --version
```

**依存関係のインストールと起動:**
```bash
# 仮想環境がアクティブな状態で実行
pip install -r requirements.txt
uvicorn app.main:app --reload
```
→ バックエンドAPI: http://localhost:8000
→ Swagger UI: http://localhost:8000/docs

**3. フロントエンド起動（別ターミナル）**
```bash
cd frontend
npm install
npm run dev
```
→ フロントエンド: http://localhost:5173

---

## 📁 プロジェクト構造

```
ai-vehicle-routing/
├── frontend/          # React + TypeScript フロントエンド
│   ├── src/
│   │   ├── components/  # UI コンポーネント
│   │   ├── pages/       # ページコンポーネント
│   │   ├── services/    # API サービス層
│   │   ├── stores/      # Zustand ステート管理
│   │   └── types/       # TypeScript 型定義
│   ├── package.json
│   └── vite.config.ts
│
├── backend/           # FastAPI バックエンド
│   ├── app/
│   │   ├── api/         # API エンドポイント
│   │   ├── models/      # SQLAlchemy モデル
│   │   ├── schemas/     # Pydantic スキーマ
│   │   ├── services/    # ビジネスロジック
│   │   └── main.py      # アプリケーション エントリーポイント
│   ├── data/            # データベース & デモデータ
│   ├── tests/           # テスト
│   └── requirements.txt
│
├── shared/            # 共有型定義（フロント・バック共通）
│   └── types/
│       └── index.ts
│
└── docs/              # ドキュメント
    ├── architecture.md     # アーキテクチャ設計書
    ├── front-end-spec.md   # UI/UX 仕様書
    └── stories/            # 開発ストーリー
```

---

## 🎯 開発ロードマップ

> **注：** 以下は最終デモの計画機能です。現在は Story 001（プロジェクト初期化）が完了した段階です。

### Story 001: プロジェクト初期化 ✅ 完了
- ✅ Monorepo 構造作成
- ✅ バックエンド骨格（FastAPI + 基本エンドポイント）
- ✅ フロントエンド骨格（React + TypeScript + Vite）
- ✅ 共有型定義
- ✅ デモデータテンプレート

### Story 002-004: コア機能開発（予定）
**1. 最適化エンジン（Story 002）**
- Google OR-Tools CVRPTW 実装
- 車両容量制約（重量・容積）
- 時間窓制約（午前30%、午後70%）
- 複数拠点対応
- `/api/v1/optimization/optimize` エンドポイント

**2. ビジュアル化（Story 003）**
- OpenStreetMapでのルート表示
- 10色の車両ルートカラーリング
- 地図コンポーネント実装

**3. コスト分析（Story 004）**
- 最適化前後の比較ダッシュボード
- 距離・時間・コスト削減率計算
- 結果表示UI

---

## 📊 デモデータ

- **拠点:** 4箇所（東京都心部、20km範囲内）
- **車両:** 10台（2t車×5、4t車×5）
- **配送先:** 100件（50km範囲内）
- **時間窓:** 午前30件、午後70件

---

## 🧪 テスト

**バックエンドテスト:**
```bash
cd backend
pytest
```

**フロントエンドテスト:**
```bash
cd frontend
npm run test
```

---

## 📚 ドキュメント

- [アーキテクチャ設計書](docs/architecture.md) - システム全体の技術設計
- [UI/UX仕様書](docs/front-end-spec.md) - フロントエンド詳細仕様
- [API仕様](http://localhost:8000/docs) - Swagger UI（起動後アクセス）

---

## 🛠️ 開発コマンド

### バックエンド
```bash
# 開発サーバー起動（ホットリロード）
uvicorn app.main:app --reload

# データベース初期化
python scripts/init_db.py

# デモデータ投入
python scripts/seed_demo_data.py

# テスト実行
pytest

# コードフォーマット
black app/
```

### フロントエンド
```bash
# 開発サーバー起動
npm run dev

# 本番ビルド
npm run build

# ビルド結果のプレビュー
npm run preview

# テスト実行
npm run test

# リント
npm run lint
```

---

## 🎨 UI/UX 設計方針

> **注：** 以下は最終デモの UI/UX 設計方針です（`docs/front-end-spec.md` 参照）

- **日本語UI:** 日本市場向けのローカライズ
- **投影モード:** 大画面デモ用の高コントラスト表示（予定）
- **ワンクリックデモ:** 最小限の操作で最適化実行（予定）
- **段階的情報開示:** 初期画面はシンプル、詳細は必要時に表示（予定）

**現在の実装：** 基本的な React アプリケーション骨格のみ

---

## 🔧 トラブルシューティング

### バックエンドが起動しない

**Python バージョンの確認:**
```bash
# 仮想環境内のPythonバージョンを確認（3.11.xである必要がある）
python --version

# システムのPythonバージョン（開発用、任意でOK）
py --version  # Windows
python3 --version  # macOS/Linux
```

**仮想環境の再作成:**
```bash
cd backend
# 既存の仮想環境を削除
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Python 3.11で仮想環境を再作成
py -3.11 -m venv venv  # Windows
python3.11 -m venv venv  # macOS/Linux

# 仮想環境をアクティブ化
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# 依存関係の再インストール
pip install --upgrade pip
pip install -r requirements.txt
```

**OR-Tools インストールエラーの場合:**
```bash
# Python 3.11が正しくインストールされているか確認
py -3.11 --version  # Windows
python3.11 --version  # macOS/Linux

# Python 3.11がない場合はインストール
# Windows: https://www.python.org/downloads/
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11 python3.11-venv
```

### フロントエンドが起動しない
```bash
# Node.js バージョン確認
node --version  # 18+ 必要

# node_modules 削除して再インストール
rm -rf node_modules
npm install
```

### 共有型のインポートエラー
```bash
# Vite config の確認（vite.config.ts）
# server.fs.allow: ['..'] が設定されているか確認
```

---

## 📄 ライセンス

このプロジェクトは演示用プロトタイプです。

---

## 👥 チーム

- **アーキテクト:** Winston
- **UXデザイナー:** Sally
- **開発者:** James

---

**最終更新:** 2025-10-30
**バージョン:** 1.0.0（Story 001 完了）
**ステータス:** 🚧 初期化フェーズ完了、コア機能開発中（Story 002予定）

**重要：** 本プロジェクトは **Python 3.11 仮想環境** が必須です。Python 3.12+では OR-Tools が動作しません。
