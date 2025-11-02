# Story 003: フロントエンド統合 - 開発計画

**作成日:** 2025-11-03
**前提条件:** Story 002 完了（Backend API 実装済み）
**目標:** React フロントエンドと Backend API の統合、配車結果の可視化

---

## 📋 Story 概要

### 目的

Story 002 で実装した Backend API と連携する React フロントエンドアプリケーションを構築し、
ユーザーが直感的に VRP 最適化結果を確認できる Demo 用 UI を提供する。

### 主要機能

1. **地図表示** - OpenStreetMap + Leaflet による配送点・ルート可視化
2. **データ入力** - 拠点・車両・配送先の選択インターフェース
3. **最適化実行** - Backend API `/api/v1/optimization/optimize` 呼び出し
4. **結果表示** - 最適化ルート、改善指標、コスト比較の可視化
5. **インタラクティブ機能** - ルート選択、配送点詳細表示

---

## 🎯 技術仕様

### Frontend Tech Stack（確定版）

| Technology | Version | Purpose |
|------------|---------|---------|
| TypeScript | 5.3+ | 型安全な開発 |
| React | 18.2+ | UI フレームワーク |
| Ant Design | 5.12+ | UI コンポーネント |
| Zustand | 4.4+ | 状態管理 |
| React Router | 6.21+ | ルーティング |
| Leaflet | 1.9+ | 地図表示 |
| React-Leaflet | 4.2+ | React Leaflet ラッパー |
| Axios | 1.6+ | HTTP Client |
| Recharts | 2.10+ | グラフ表示 |
| Vite | 5.0+ | ビルドツール |

### Backend API（Story 002 実装済み）

**Base URL:** `http://localhost:8000`

**使用エンドポイント:**
1. `POST /api/v1/seed/demo-data` - デモデータ初期化
2. `GET /api/v1/depots` - 拠点リスト取得
3. `GET /api/v1/vehicles?depot_id={id}` - 車両リスト取得
4. `GET /api/v1/deliveries?time_window={morning|afternoon}` - 配送先リスト取得
5. `POST /api/v1/optimization/optimize` - **VRP 最適化実行（同期）**

**重要:** Story 002 では**同期 API**を採用（2-30秒で結果返却）

---

## 📐 UI/UX 設計

### ページ構成

```
/ (Home)
├── Layout (Ant Design Layout)
│   ├── Header (タイトル + ナビゲーション)
│   ├── Sider (左: 操作パネル)
│   │   ├── データ初期化ボタン
│   │   ├── 拠点選択
│   │   ├── 車両選択（複数）
│   │   ├── 配送先選択（複数）
│   │   └── 最適化実行ボタン
│   └── Content (右: 地図 + 結果表示)
│       ├── 地図エリア (Leaflet)
│       │   ├── 拠点マーカー（青）
│       │   ├── 配送先マーカー（赤）
│       │   └── 最適化ルート（色分け）
│       └── 結果パネル (下部/タブ)
│           ├── 改善指標（カード表示）
│           ├── ルート一覧（Table）
│           └── コスト比較（Chart）
```

### UI コンポーネント構成

```
src/
├── components/
│   ├── Layout/
│   │   ├── AppLayout.tsx        # メインレイアウト
│   │   ├── Header.tsx            # ヘッダー
│   │   └── Sider.tsx             # サイドバー
│   ├── Map/
│   │   ├── MapView.tsx           # 地図コンポーネント
│   │   ├── DepotMarker.tsx       # 拠点マーカー
│   │   ├── DeliveryMarker.tsx    # 配送点マーカー
│   │   └── RoutePolyline.tsx     # ルート線
│   ├── Control/
│   │   ├── DataInitializer.tsx   # データ初期化ボタン
│   │   ├── DepotSelector.tsx     # 拠点選択
│   │   ├── VehicleSelector.tsx   # 車両選択
│   │   ├── DeliverySelector.tsx  # 配送先選択
│   │   └── OptimizeButton.tsx    # 最適化実行ボタン
│   └── Result/
│       ├── ResultPanel.tsx       # 結果パネル
│       ├── ImprovementCards.tsx  # 改善指標カード
│       ├── RouteTable.tsx        # ルート一覧テーブル
│       └── CostChart.tsx         # コスト比較チャート
├── services/
│   └── api.ts                    # API Client（Axios）
├── stores/
│   └── useVRPStore.ts            # Zustand Store
├── types/
│   └── index.ts                  # TypeScript 型定義
├── App.tsx                       # ルートコンポーネント
└── main.tsx                      # エントリーポイント
```

---

## 🔧 実装タスク

### Task 1: TypeScript 型定義 ⏳

**目的:** Backend API レスポンスの型を定義

**成果物:** `src/types/index.ts`

**主要型:**
```typescript
// 拠点
export interface Depot {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  operating_hours: {
    start_time: string;
    end_time: string;
  };
}

// 車両
export interface Vehicle {
  id: string;
  vehicle_type: string;
  capacity_weight: number;
  capacity_volume: number;
  depot_id: string;
  available_hours: {
    start_time: string;
    end_time: string;
  };
  cost_per_km: number;
  cost_per_hour: number;
}

// 配送先
export interface Delivery {
  id: string;
  customer_name: string;
  latitude: number;
  longitude: number;
  address: string;
  package_count: number;
  weight: number;
  volume: number;
  time_window: 'morning' | 'afternoon' | null;
  service_time: number;
}

// ルート停車点
export interface RouteStop {
  delivery_id: string;
  sequence: number;
  arrival_time: string;
  departure_time: string;
  distance_from_previous: number;
  duration_from_previous: number;
}

// ルート
export interface Route {
  id: string;
  vehicle_id: string;
  depot_id: string;
  stops: RouteStop[];
  total_distance: number;
  total_duration: number;
  total_weight: number;
  total_volume: number;
  total_cost: number;
  utilization_weight: number;
  utilization_volume: number;
}

// 基线指标
export interface BaselineMetrics {
  total_distance: number;
  total_duration: number;
  total_cost: number;
  average_utilization_weight: number;
  method: string;
}

// 改善指标
export interface ImprovementMetrics {
  distance_reduction_km: number;
  distance_reduction_percent: number;
  duration_reduction_minutes: number;
  cost_reduction_amount: number;
  cost_reduction_percent: number;
  utilization_improvement_percent: number;
}

// 最適化結果
export interface OptimizationResult {
  id: string;
  request_id: string;
  routes: Route[];
  total_distance: number;
  total_duration: number;
  total_cost: number;
  average_utilization_weight: number;
  average_utilization_volume: number;
  computation_time: number;
  unassigned_deliveries: string[];
  baseline_metrics: BaselineMetrics;
  improvement_metrics: ImprovementMetrics;
  created_at: string;
}

// API Request
export interface OptimizationRequest {
  depot_ids: string[];
  vehicle_ids: string[];
  delivery_ids: string[];
}
```

---

### Task 2: API Client 封装 ⏳

**目的:** Axios による API 呼び出しラッパー

**成果物:** `src/services/api.ts`

**主要関数:**
```typescript
import axios from 'axios';
import type {
  Depot,
  Vehicle,
  Delivery,
  OptimizationRequest,
  OptimizationResult,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 35000, // 30秒 API + 5秒マージン
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // デモデータ初期化
  initDemoData: () =>
    apiClient.post('/seed/demo-data'),

  // 拠点リスト取得
  getDepots: () =>
    apiClient.get<{ depots: Depot[]; total: number }>('/depots'),

  // 車両リスト取得
  getVehicles: (depotId?: string) =>
    apiClient.get<{ vehicles: Vehicle[]; total: number }>('/vehicles', {
      params: depotId ? { depot_id: depotId } : {},
    }),

  // 配送先リスト取得
  getDeliveries: (timeWindow?: 'morning' | 'afternoon') =>
    apiClient.get<{ deliveries: Delivery[]; total: number }>('/deliveries', {
      params: timeWindow ? { time_window: timeWindow } : {},
    }),

  // VRP 最適化実行（同期）
  optimize: (request: OptimizationRequest) =>
    apiClient.post<OptimizationResult>('/optimization/optimize', request),
};
```

---

### Task 3: Zustand 状態管理設定 ⏳

**目的:** グローバル状態管理

**成果物:** `src/stores/useVRPStore.ts`

**状態定義:**
```typescript
import { create } from 'zustand';
import type {
  Depot,
  Vehicle,
  Delivery,
  OptimizationResult,
} from '../types';

interface VRPStore {
  // データ
  depots: Depot[];
  vehicles: Vehicle[];
  deliveries: Delivery[];
  optimizationResult: OptimizationResult | null;

  // 選択状態
  selectedDepotIds: string[];
  selectedVehicleIds: string[];
  selectedDeliveryIds: string[];

  // UI状態
  loading: boolean;
  error: string | null;

  // アクション
  setDepots: (depots: Depot[]) => void;
  setVehicles: (vehicles: Vehicle[]) => void;
  setDeliveries: (deliveries: Delivery[]) => void;
  setOptimizationResult: (result: OptimizationResult | null) => void;

  toggleDepot: (id: string) => void;
  toggleVehicle: (id: string) => void;
  toggleDelivery: (id: string) => void;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  reset: () => void;
}

export const useVRPStore = create<VRPStore>((set) => ({
  // 初期状態
  depots: [],
  vehicles: [],
  deliveries: [],
  optimizationResult: null,
  selectedDepotIds: [],
  selectedVehicleIds: [],
  selectedDeliveryIds: [],
  loading: false,
  error: null,

  // アクション実装
  setDepots: (depots) => set({ depots }),
  setVehicles: (vehicles) => set({ vehicles }),
  setDeliveries: (deliveries) => set({ deliveries }),
  setOptimizationResult: (result) => set({ optimizationResult: result }),

  toggleDepot: (id) => set((state) => ({
    selectedDepotIds: state.selectedDepotIds.includes(id)
      ? state.selectedDepotIds.filter((i) => i !== id)
      : [...state.selectedDepotIds, id],
  })),

  toggleVehicle: (id) => set((state) => ({
    selectedVehicleIds: state.selectedVehicleIds.includes(id)
      ? state.selectedVehicleIds.filter((i) => i !== id)
      : [...state.selectedVehicleIds, id],
  })),

  toggleDelivery: (id) => set((state) => ({
    selectedDeliveryIds: state.selectedDeliveryIds.includes(id)
      ? state.selectedDeliveryIds.filter((i) => i !== id)
      : [...state.selectedDeliveryIds, id],
  })),

  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  reset: () => set({
    optimizationResult: null,
    selectedDepotIds: [],
    selectedVehicleIds: [],
    selectedDeliveryIds: [],
    error: null,
  }),
}));
```

---

### Task 4: ルート・レイアウト設定 ⏳

**目的:** Ant Design Layout によるページ構成

**成果物:**
- `src/components/Layout/AppLayout.tsx`
- `src/App.tsx`

**レイアウト構成:**
```tsx
<Layout style={{ minHeight: '100vh' }}>
  <Header>AI自動配車システム Demo</Header>
  <Layout>
    <Sider width={320}>
      {/* 操作パネル */}
      <DataInitializer />
      <Divider />
      <DepotSelector />
      <VehicleSelector />
      <DeliverySelector />
      <Divider />
      <OptimizeButton />
    </Sider>
    <Content>
      {/* 地図 + 結果表示 */}
      <MapView />
      {optimizationResult && <ResultPanel />}
    </Content>
  </Layout>
</Layout>
```

---

### Task 5: 地図コンポーネント実装 ⏳

**目的:** Leaflet による地図表示

**成果物:**
- `src/components/Map/MapView.tsx`
- `src/components/Map/DepotMarker.tsx`
- `src/components/Map/DeliveryMarker.tsx`
- `src/components/Map/RoutePolyline.tsx`

**地図設定:**
- **中心:** 東京（35.6812, 139.7671）
- **ズーム:** 11
- **タイル:** OpenStreetMap

**マーカー:**
- **拠点:** 青色アイコン
- **配送先（morning）:** 赤色アイコン
- **配送先（afternoon）:** オレンジ色アイコン
- **配送先（anytime）:** 緑色アイコン

**ルート線:**
- 車両ごとに異なる色（例: #1f77b4, #ff7f0e, #2ca02c）
- 線幅: 3px
- 透明度: 0.7

---

### Task 6: 操作パネル実装 ⏳

**目的:** データ選択と最適化実行

**成果物:**
- `src/components/Control/DataInitializer.tsx`
- `src/components/Control/DepotSelector.tsx`
- `src/components/Control/VehicleSelector.tsx`
- `src/components/Control/DeliverySelector.tsx`
- `src/components/Control/OptimizeButton.tsx`

**UI要素:**
- **DataInitializer:** Button（`POST /seed/demo-data`）
- **DepotSelector:** Checkbox.Group
- **VehicleSelector:** Checkbox.Group（depot_id でフィルタ）
- **DeliverySelector:** Checkbox.Group（time_window でフィルタ）
- **OptimizeButton:** Button（Primary、Loading 対応）

---

### Task 7: 結果表示実装 ⏳

**目的:** 最適化結果の可視化

**成果物:**
- `src/components/Result/ResultPanel.tsx`
- `src/components/Result/ImprovementCards.tsx`
- `src/components/Result/RouteTable.tsx`
- `src/components/Result/CostChart.tsx`

**改善指標カード:**
```tsx
<Row gutter={16}>
  <Col span={6}>
    <Statistic
      title="距離削減"
      value={improvement_metrics.distance_reduction_percent}
      suffix="%"
      prefix={<ArrowDownOutlined />}
    />
  </Col>
  <Col span={6}>
    <Statistic
      title="コスト削減"
      value={improvement_metrics.cost_reduction_percent}
      suffix="%"
      prefix={<DollarOutlined />}
    />
  </Col>
  <Col span={6}>
    <Statistic
      title="積載率改善"
      value={improvement_metrics.utilization_improvement_percent}
      suffix="%"
      prefix={<RiseOutlined />}
    />
  </Col>
  <Col span={6}>
    <Statistic
      title="計算時間"
      value={computation_time / 1000}
      suffix="秒"
    />
  </Col>
</Row>
```

**ルート一覧テーブル:**
- 列: ルートID、車両、停車数、総距離、総時間、積載率
- 行クリックで地図上でハイライト

**コスト比較チャート:**
- Recharts BarChart
- 基線 vs 最適化後のコスト比較

---

### Task 8: 統合テスト ⏳

**目的:** フロントエンド・バックエンド統合動作確認

**確認項目:**
1. ✅ デモデータ初期化成功
2. ✅ 拠点・車両・配送先リスト取得成功
3. ✅ VRP 最適化実行成功（30秒以内）
4. ✅ 地図上にルート表示
5. ✅ 改善指標カード表示
6. ✅ ルート一覧テーブル表示
7. ✅ コスト比較チャート表示
8. ✅ エラーハンドリング（API エラー時）

---

## 📊 工数見積

| Task | 内容 | 見積工数 |
|------|------|---------|
| Task 1 | TypeScript 型定義 | 0.5日 |
| Task 2 | API Client 封装 | 0.5日 |
| Task 3 | Zustand 状態管理 | 1日 |
| Task 4 | ルート・レイアウト | 0.5日 |
| Task 5 | 地図コンポーネント | 2日 |
| Task 6 | 操作パネル | 1.5日 |
| Task 7 | 結果表示 | 1.5日 |
| Task 8 | 統合テスト | 0.5日 |
| **合計** | | **8日** |

---

## 🚀 開始準備

### 環境確認

```bash
# Node.js バージョン確認
node --version  # 18+ 推奨

# 依存インストール
cd frontend
npm install

# 開発サーバー起動
npm run dev
```

### Backend 起動（前提）

```bash
cd backend
uvicorn app.main:app --reload
# → http://localhost:8000
```

---

## 📝 Next Steps

1. ✅ Story 003 計画承認
2. ⏳ Task 1 開始: TypeScript 型定義
3. ⏳ Task 2-8 順次実装
4. ✅ Demo 動作確認

---

**作成者:** 開発チーム
**状態:** 📋 計画策定完了、実装開始準備中
**最終更新:** 2025-11-03
