# Story 002 技術決策分析
## VRP優化エンジン実装範囲とAPI設計

**作成日:** 2025-10-30
**対象:** Story 002（最適化エンジン実装）
**決定者:** 開発チーム

---

## 📋 決策総覧

| 決策項目 | 決定内容 | 状態 |
|---------|---------|------|
| **API設計方式** | 同期簡化Demo | ✅ 確定 |
| **優化算法実装範囲** | 待決策 | 🔍 分析中 |
| **API契約定義** | 待決策 | 🔍 分析中 |

---

## 1. API設計方式：同期簡化Demo ✅

### 確認決策

**採用方式：** 同期REST API（非異步タスクキュー）

**理由：**
- ✅ **デモ要件に十分：** 100配送点の計算時間は2-5秒、ユーザー許容範囲内
- ✅ **実装複雑度低：** タスクキュー、進捗追跡、データベース永続化不要
- ✅ **デバッグ容易：** リクエスト-レスポンス直接対応、エラー追跡簡単
- ✅ **インフラ不要：** Celery/RQ/Redis等の追加依存なし

**影響：**
- 📝 **共有型定義簡略化：** `OptimizationTask`、`TaskStatus` 等の型定義使用不要
- 📝 **API端点簡略化：** `/optimize` 1個のみ、`/tasks/{id}` 不要
- 📝 **エラーハンドリング簡略化：** HTTPステータスコードで直接返却

---

## 2. 優化算法実装範囲 🔍

### 現状分析

**architecture.mdの設計：**
- 3つのアルゴリズム選択肢：`greedy`、`genetic`、`exact`
- OR-Tools CVRPTW（容量制約+時間窓口）
- 最適化前のベースライン計算（貪欲法）
- 改善メトリクス計算（削減率比較）

**共有型定義の期待：**
```typescript
type Algorithm = "greedy" | "genetic" | "exact"
interface OptimizationRequest {
  algorithm: Algorithm
  optimization_strategy: OptimizationStrategy // "distance" | "time" | "cost"
}
```

---

### 方案1: ミニマル実装（OR-Tools 標準ソルバーのみ）

**推奨度:** ⭐⭐⭐⭐⭐ (95点) - **最推奨**

#### 実装内容

**アルゴリズム：**
- ✅ **OR-Tools標準CVRPTW ソルバー** （路径引導局所搜索）
- ❌ 3つのアルゴリズム選択肢（greedy/genetic/exact）- 使用しない
- ✅ 距離最適化のみ（`optimization_strategy: "distance"` 固定）

**制約条件：**
- ✅ 車両容量制約（重量・体積）
- ✅ 時間窓口制約（午前30%、午後70%）
- ✅ 複数拠点対応
- ✅ サービス時間考慮

**ベースライン計算：**
- ✅ 単純割当法（simple_assignment）- 最近接車両に順次割当
- ✅ 改善メトリクス計算（距離/時間/コスト削減率）

**OR-Tools設定：**
```python
from ortools.constraint_solver import routing_enums_pb2

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)
search_parameters.time_limit.seconds = 10  # 10秒タイムリミット
```

#### メリット

1. **実装速度:** 2-3日で完成可能
2. **安定性:** OR-Tools標準設定、実績豊富
3. **性能:** 100配送点で2-5秒、デモに十分
4. **保守性:** コード量少、デバッグ容易
5. **拡張性:** 将来的にアルゴリズム追加可能（インターフェース変更不要）

#### デメリット

1. **柔軟性:** 1つのアルゴリズムのみ、比較デモ不可
2. **教育価値:** 異なるアルゴリズムの性能比較を見せられない

#### API変更

```typescript
// Request - algorithm パラメータ削除
interface OptimizationRequest {
  depot_ids: string[]
  vehicle_ids: string[]
  delivery_ids: string[]
  // optimization_strategy: "distance" 固定（パラメータ不要）
}

// Result - baseline.method を "simple_assignment" 固定
interface BaselineMetrics {
  method: "simple_assignment"  // 固定値
  // ...
}
```

#### 工数見積

| タスク | 工数 |
|-------|-----|
| VRPソルバー実装 | 1日 |
| ベースライン計算 | 0.5日 |
| メトリクス計算 | 0.5日 |
| テスト | 1日 |
| **合計** | **3日** |

---

### 方案2: 拡張実装（3アルゴリズム + 3最適化戦略）

**推奨度:** ⭐⭐⭐ (70点) - オーバーエンジニアリングリスク

#### 実装内容

**アルゴリズム：**
- ✅ **Greedy（貪欲法）** - 最近接挿入法
- ✅ **Genetic（遺伝的アルゴリズム）** - OR-Tools Guided Local Search
- ✅ **Exact（厳密解）** - OR-Tools Mixed Integer Programming（小規模のみ）

**最適化戦略：**
- ✅ `distance` - 総走行距離最小化
- ✅ `time` - 総所要時間最小化
- ✅ `cost` - 総コスト最小化（距離コスト + 時間コスト）

**ベースライン計算：**
- ✅ アルゴリズム毎に異なるベースライン
  - Greedy → 単純割当
  - Genetic → Greedy結果
  - Exact → Genetic結果

#### メリット

1. **教育価値:** アルゴリズム比較デモが可能
2. **柔軟性:** 様々なシナリオ対応
3. **デザイン忠実度:** architecture.md の設計通り

#### デメリット

1. **実装複雑度:** 4-5倍の工数（約15日）
2. **テスト負荷:** 3×3=9パターンのテストケース
3. **バグリスク:** 複雑なロジック、エッジケース多数
4. **デモ価値不明確:** 顧客は「1つの良い解」が見たい、比較は不要の可能性
5. **パフォーマンス:** Exact解は30配送点以上で実用不可

#### API変更

```typescript
// architecture.md の設計通り
interface OptimizationRequest {
  depot_ids: string[]
  vehicle_ids: string[]
  delivery_ids: string[]
  optimization_strategy: "distance" | "time" | "cost"
  algorithm: "greedy" | "genetic" | "exact"
}
```

#### 工数見積

| タスク | 工数 |
|-------|-----|
| Greedy実装 | 2日 |
| Genetic（GLS）実装 | 2日 |
| Exact（MIP）実装 | 3日 |
| 3戦略対応（distance/time/cost） | 2日 |
| ベースライン計算（複数方式） | 1日 |
| メトリクス計算 | 1日 |
| テスト（9パターン） | 4日 |
| **合計** | **15日** |

---

### 方案3: 段階実装（Phase 1: ミニマル → Phase 2: 拡張）

**推奨度:** ⭐⭐⭐⭐ (85点) - リスク分散

#### 実装戦略

**Phase 1（Story 002）: ミニマル実装**
- 方案1と同じ（3日）
- デモ可能な動作版を迅速に完成

**Phase 2（Story 005 等）: アルゴリズム拡張**
- ユーザーフィードバック後に判断
- 必要であれば3アルゴリズム対応追加

#### メリット

1. **リスク管理:** 早期にデモ可能版完成
2. **柔軟性:** ユーザーフィードバックで方向修正可能
3. **投資効率:** 不要機能への過剰投資回避

#### デメリット

1. **リファクタリング:** Phase 2で一部コード再設計必要
2. **設計先読み:** Phase 2を見越したインターフェース設計必要

---

### 推奨決策

**推奨:** ✅ **方案1: ミニマル実装**

**理由：**

1. **デモ目標達成:** 「AIによる配車効率化」を視覚的に証明できれば十分
2. **YAGNI原則:** 3アルゴリズム比較は現時点で要件にない
3. **リリース速度:** 3日で完成、顧客への早期価値提供
4. **技術リスク低:** OR-Tools標準機能のみ、枯れた技術
5. **保守コスト低:** シンプルなコード、長期保守容易

**将来の拡張パス:**
- ユーザーが「アルゴリズム比較機能」を要求した場合、Story 005で追加
- その時点で方案2の要素を段階的に実装

---

## 3. API契約定義 🔍

### 方案A: ミニマル同期API（方案1対応）

**推奨度:** ⭐⭐⭐⭐⭐ (95点) - **最推奨**

#### API Endpoints

**1. POST /api/v1/optimization/optimize（VRP最適化実行）**

**Request:**
```json
{
  "depot_ids": ["depot-1", "depot-2", "depot-3", "depot-4"],
  "vehicle_ids": ["vehicle-1", "vehicle-2", ..., "vehicle-10"],
  "delivery_ids": ["delivery-1", "delivery-2", ..., "delivery-100"]
}
```

**Response (200 OK - 同期返却):**
```json
{
  "id": "result-abc-123",
  "request_id": "req-xyz-456",
  "routes": [
    {
      "id": "route-1",
      "vehicle_id": "vehicle-1",
      "depot_id": "depot-1",
      "stops": [
        {
          "delivery_id": "delivery-5",
          "sequence": 1,
          "arrival_time": "2025-10-30T09:15:00Z",
          "departure_time": "2025-10-30T09:25:00Z",
          "distance_from_previous": 3.2,
          "duration_from_previous": 15
        }
      ],
      "total_distance": 45.3,
      "total_duration": 240,
      "total_weight": 1500,
      "total_volume": 8.5,
      "total_cost": 15000,
      "utilization_weight": 75.0,
      "utilization_volume": 85.0
    }
  ],
  "total_distance": 450.0,
  "total_duration": 2400,
  "total_cost": 150000,
  "average_utilization_weight": 72.5,
  "average_utilization_volume": 80.0,
  "computation_time": 3500,
  "unassigned_deliveries": [],
  "baseline_metrics": {
    "total_distance": 600.0,
    "total_duration": 3200,
    "total_cost": 200000,
    "average_utilization_weight": 60.0,
    "method": "simple_assignment"
  },
  "improvement_metrics": {
    "distance_reduction_km": 150.0,
    "distance_reduction_percent": 25.0,
    "duration_reduction_minutes": 800,
    "cost_reduction_amount": 50000,
    "cost_reduction_percent": 25.0,
    "utilization_improvement_percent": 12.5
  },
  "created_at": "2025-10-30T08:00:00Z"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "車両数が配送点数より少なすぎます",
    "details": "10台の車両で100配送点は割当不可能"
  }
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": {
    "code": "OPTIMIZATION_FAILED",
    "message": "最適化計算がタイムアウトしました",
    "details": "10秒以内に解が見つかりませんでした"
  }
}
```

---

**2. GET /api/v1/depots（据点リスト取得）**

**Response:**
```json
{
  "depots": [
    {
      "id": "depot-1",
      "name": "東京物流センター",
      "latitude": 35.6812,
      "longitude": 139.7671,
      "address": "東京都千代田区",
      "operating_hours": {
        "start_time": "08:00",
        "end_time": "20:00"
      }
    }
  ]
}
```

---

**3. GET /api/v1/vehicles（車両リスト取得）**

**Query Parameters:**
- `depot_id` (optional) - 据点IDでフィルタ

**Response:**
```json
{
  "vehicles": [
    {
      "id": "vehicle-1",
      "vehicle_type": "2t",
      "capacity_weight": 2000,
      "capacity_volume": 10.0,
      "depot_id": "depot-1",
      "available_hours": {
        "start_time": "08:00",
        "end_time": "18:00"
      },
      "cost_per_km": 50,
      "cost_per_hour": 3000
    }
  ]
}
```

---

**4. GET /api/v1/deliveries（配送点リスト取得）**

**Query Parameters:**
- `time_window` (optional) - "morning" | "afternoon" でフィルタ

**Response:**
```json
{
  "deliveries": [
    {
      "id": "delivery-1",
      "customer_name": "顧客A",
      "latitude": 35.6895,
      "longitude": 139.6917,
      "address": "東京都新宿区",
      "package_count": 2,
      "weight": 150,
      "volume": 1.5,
      "time_window": "morning",
      "service_time": 10
    }
  ]
}
```

---

**5. POST /api/v1/seed/demo-data（デモデータ初期化）**

**Request:** (empty body)

**Response (201 Created):**
```json
{
  "message": "デモデータを初期化しました",
  "summary": {
    "depots": 4,
    "vehicles": 10,
    "deliveries": 100
  }
}
```

---

#### 実装詳細

**FastAPI実装例:**
```python
from fastapi import APIRouter, HTTPException
from app.schemas import OptimizationRequest, OptimizationResult
from app.services.vrp_service import VRPService

router = APIRouter(prefix="/api/v1/optimization", tags=["optimization"])

@router.post("/optimize", response_model=OptimizationResult)
async def optimize_routes(request: OptimizationRequest):
    """
    VRP最適化実行（同期）

    - 2-5秒で結果返却
    - タイムアウト: 10秒
    """
    try:
        vrp_service = VRPService()
        result = vrp_service.optimize(
            depot_ids=request.depot_ids,
            vehicle_ids=request.vehicle_ids,
            delivery_ids=request.delivery_ids
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail={
            "code": "INVALID_REQUEST",
            "message": str(e)
        })
    except TimeoutError:
        raise HTTPException(status_code=500, detail={
            "code": "OPTIMIZATION_TIMEOUT",
            "message": "最適化計算がタイムアウトしました"
        })
```

---

### 方案B: 完全設計API（architecture.md通り）

**推奨度:** ⭐⭐ (40点) - 過剰設計

#### API Endpoints

architecture.mdの異步設計通り：
- POST `/api/v1/optimization/optimize` → 返回 `task_id`
- GET `/api/v1/optimization/tasks/{task_id}` → 返回進捗状態
- GET `/api/v1/optimization/results/{id}` → 返回結果

**理由で非推奨:**
- 同期APIで十分（2-5秒）
- タスクキュー実装不要
- デモには過剰

---

### 推奨決策

**推奨:** ✅ **方案A: ミニマル同期API**

**API Endpoints 最終版:**
1. ✅ `POST /api/v1/optimization/optimize` - VRP最適化実行（同期）
2. ✅ `GET /api/v1/depots` - 据点リスト
3. ✅ `GET /api/v1/vehicles` - 車両リスト
4. ✅ `GET /api/v1/deliveries` - 配送点リスト
5. ✅ `POST /api/v1/seed/demo-data` - デモデータ初期化

**特徴:**
- シンプル、実装容易
- デモ要件に完全対応
- テスト容易
- エラーハンドリング明確

---

## 📋 最終推奨

### 優先順位

| 順位 | 推奨内容 | 推奨度 | 理由 |
|-----|---------|-------|------|
| 1 | **方案1: ミニマル算法実装** | ⭐⭐⭐⭐⭐ | 3日完成、リスク最小、デモに十分 |
| 2 | **方案A: ミニマル同期API** | ⭐⭐⭐⭐⭐ | シンプル、保守容易、要件満足 |
| 3 | 方案3: 段階実装 | ⭐⭐⭐⭐ | リスク分散、柔軟性高 |
| 4 | 方案2: 拡張算法実装 | ⭐⭐⭐ | 工数15日、現時点で不要 |

### 工数見積（推奨方案）

**Story 002: 最適化エンジン実装**

| タスク | 工数 |
|-------|-----|
| 1. API端点実装（5個） | 1日 |
| 2. OR-Tools VRPソルバー実装 | 1.5日 |
| 3. ベースライン計算実装 | 0.5日 |
| 4. メトリクス計算実装 | 0.5日 |
| 5. デモデータ投入スクリプト | 0.5日 |
| 6. 単体テスト | 1日 |
| 7. 統合テスト | 1日 |
| **合計** | **6日** |

### Next Steps

1. ✅ **確認推奨方案** - 開発チームで合意形成
2. 📝 **Story 002作成** - タスク詳細化
3. 💻 **実装開始** - API → VRPソルバー → テスト
4. 🧪 **統合テスト** - フロントエンド連携確認

---

## 付録：参考資料

### OR-Tools CVRPTW 参考実装

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def create_data_model():
    """VRPデータモデル作成"""
    data = {}
    data['distance_matrix'] = [...]  # 距離行列
    data['time_matrix'] = [...]      # 時間行列
    data['time_windows'] = [...]     # 時間窓口
    data['demands'] = [...]          # 需要（重量）
    data['vehicle_capacities'] = [...] # 車両容量
    data['num_vehicles'] = 10
    data['depot'] = 0
    return data

def solve_vrp(data):
    """VRP求解"""
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )
    routing = pywrapcp.RoutingModel(manager)

    # 距離コールバック
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 容量制約
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],
        True,  # start cumul to zero
        'Capacity'
    )

    # 時間窓口制約
    time_callback_index = routing.RegisterTransitCallback(
        lambda from_idx, to_idx: data['time_matrix'][
            manager.IndexToNode(from_idx)
        ][manager.IndexToNode(to_idx)]
    )
    routing.AddDimension(
        time_callback_index,
        30,  # 待機時間許容
        180, # 最大ルート時間
        False,
        'Time'
    )
    time_dimension = routing.GetDimensionOrDie('Time')
    for location_idx, time_window in enumerate(data['time_windows']):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # 検索パラメータ
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = 10

    # 求解
    solution = routing.SolveWithParameters(search_parameters)
    return solution, routing, manager
```

---

**文档版本:** v1.0
**最終更新:** 2025-10-30
