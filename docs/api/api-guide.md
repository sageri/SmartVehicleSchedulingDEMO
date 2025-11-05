# API端点 開発ガイド

## 📁 ファイル構成

```
backend/app/api/v1/
├── __init__.py              # APIルーター統合
├── seed.py                  # デモデータ生成
├── depots.py                # 拠点API
├── vehicles.py              # 車両API
├── deliveries.py            # 配送先API
└── optimization.py          # VRP最適化API（核心）
```

---

## 🎯 実装済みエンドポイント（5個）

### 1. POST /api/v1/seed/demo-data
**デモデータ初期化**

- **目的:** 開発・テスト用のデモデータを生成
- **生成データ (Epic 005):**
  - 拠点: 2件（東京デポ・さいたま市デポ）
  - 車両: 5台（2t × 4, 4t × 1）
  - 配送先: 30件（東京20件 + さいたま市10件）

**リクエスト:**
```bash
curl -X POST http://localhost:8000/api/v1/seed/demo-data
```

**レスポンス:**
```json
{
  "message": "デモデータを作成しました",
  "detail": "拠点: 2件, 車両: 5台, 配送先: 30件"
}
```

**注:** デモデータはMulti-Depot VRPを実証するように設計されています（Epic 005）。
- 配送先30件、2拠点配置（東京20件 + さいたま市10件）
- 拠点制約: 各車両は所属拠点の配送先のみ配送可能
- これにより、OR-Toolsが両拠点から独立したルートを生成します。

---

### 2. GET /api/v1/depots
**拠点リスト取得**

**パラメータ:**
- `skip` (int, optional): ページネーション開始位置
- `limit` (int, optional): 最大取得件数（デフォルト: 100）

**リクエスト:**
```bash
curl http://localhost:8000/api/v1/depots
```

**レスポンス:**
```json
{
  "depots": [
    {
      "id": "depot-tokyo",
      "name": "東京デポ",
      "latitude": 35.6812,
      "longitude": 139.7671,
      "address": "東京都千代田区丸の内1-1-1",
      "operating_hours": {
        "start_time": "08:00",
        "end_time": "18:00"
      }
    }
  ],
  "total": 1
}
```

---

### 3. GET /api/v1/vehicles
**車両リスト取得**

**パラメータ:**
- `depot_id` (string, optional): 拠点IDでフィルタ
- `vehicle_type` (string, optional): 車両タイプでフィルタ（"2t" | "4t"）
- `skip` (int, optional): ページネーション開始位置
- `limit` (int, optional): 最大取得件数

**リクエスト例:**
```bash
# 全車両取得
curl http://localhost:8000/api/v1/vehicles

# 拠点でフィルタ
curl "http://localhost:8000/api/v1/vehicles?depot_id=depot-tokyo"

# 車両タイプでフィルタ
curl "http://localhost:8000/api/v1/vehicles?vehicle_type=2t"
```

**レスポンス:**
```json
{
  "vehicles": [
    {
      "id": "vehicle-001",
      "vehicle_type": "2t",
      "capacity_weight": 2000.0,
      "capacity_volume": 8.0,
      "depot_id": "depot-tokyo",
      "available_hours": {
        "start_time": "08:00",
        "end_time": "18:00"
      },
      "cost_per_km": 50.0,
      "cost_per_hour": 2000.0
    }
  ],
  "total": 3
}
```

---

### 4. GET /api/v1/deliveries
**配送先リスト取得**

**パラメータ:**
- `time_window` (string, optional): 時間窓でフィルタ（"morning" | "afternoon"）
- `skip` (int, optional): ページネーション開始位置
- `limit` (int, optional): 最大取得件数

**リクエスト例:**
```bash
# 全配送先取得
curl http://localhost:8000/api/v1/deliveries

# 午前指定のみ
curl "http://localhost:8000/api/v1/deliveries?time_window=morning"

# 午後指定のみ
curl "http://localhost:8000/api/v1/deliveries?time_window=afternoon"
```

**レスポンス:**
```json
{
  "deliveries": [
    {
      "id": "delivery-001",
      "customer_name": "新宿商店A",
      "latitude": 35.6895,
      "longitude": 139.6917,
      "address": "東京都新宿区西新宿2-8-1",
      "package_count": 3,
      "weight": 280.0,
      "volume": 0.9,
      "time_window": "morning",
      "service_time": 15
    }
  ],
  "total": 20
}
```

**注 (Epic 005):** デモデータは固定配送点リスト方式を採用（実在地点30箇所）。
- 東京デポ: 新宿区役所、渋谷駅、池袋など20箇所
- さいたま市デポ: さいたま新都心、浦和駅など10箇所
- 各配送先には`depot_id`フィールドで拠点が関連付けられます。

---

### 5. POST /api/v1/optimization/optimize ⭐
**VRP最適化実行（核心）**

**目的:** OR-Tools CVRPTWアルゴリズムで最適な配送ルートを生成

**リクエストボディ:**
```json
{
  "depot_ids": ["depot-tokyo"],
  "vehicle_ids": ["vehicle-001", "vehicle-002"],
  "delivery_ids": ["delivery-001", "delivery-002", "delivery-003"]
}
```

**制約 (Epic 005):**
- ✅ 双重容量制約（重量 + 容積）
- ✅ 時間窓制約（morning: 8:00-13:00, afternoon: 12:00-18:00, anytime: 8:00-18:00）
- ✅ 拠点制約（各車両は所属拠点の配送先のみ訪問可能）
- ✅ 各配送先は1度だけ訪問

**リクエスト例:**
```bash
curl -X POST http://localhost:8000/api/v1/optimization/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "depot_ids": ["depot-tokyo"],
    "vehicle_ids": ["vehicle-001", "vehicle-002"],
    "delivery_ids": ["delivery-001", "delivery-002", "delivery-003",
                     "delivery-004", "delivery-005", "delivery-006"]
  }'
```

**レスポンス:**
```json
{
  "id": "result-uuid",
  "request_id": "request-uuid",
  "routes": [
    {
      "id": "route-uuid",
      "vehicle_id": "vehicle-001",
      "depot_id": "depot-tokyo",
      "stops": [
        {
          "delivery_id": "delivery-001",
          "sequence": 1,
          "arrival_time": "2025-11-02T08:57:00+00:00",
          "departure_time": "2025-11-02T09:12:00+00:00",
          "distance_from_previous": 6.87,
          "duration_from_previous": 13
        }
      ],
      "total_distance": 48.09,
      "total_duration": 178,
      "total_weight": 780.0,
      "total_volume": 2.5,
      "total_cost": 8337.73,
      "utilization_weight": 39.0,
      "utilization_volume": 31.25
    }
  ],
  "total_distance": 48.09,
  "total_duration": 178,
  "total_cost": 8337.73,
  "average_utilization_weight": 39.0,
  "average_utilization_volume": 31.25,
  "computation_time": 30017,
  "unassigned_deliveries": [],
  "baseline_metrics": {
    "total_distance": 43.34,
    "total_duration": 167,
    "total_cost": 7733.85,
    "average_utilization_weight": 19.5,
    "method": "simple_assignment"
  },
  "improvement_metrics": {
    "distance_reduction_km": -4.75,
    "distance_reduction_percent": -11.0,
    "duration_reduction_minutes": -11,
    "cost_reduction_amount": -603.88,
    "cost_reduction_percent": -7.8,
    "utilization_improvement_percent": 19.5
  },
  "created_at": "2025-11-02T14:30:00Z"
}
```

**エラーレスポンス:**

- **400 Bad Request:** 指定されたIDが見つからない
```json
{
  "detail": "拠点ID depot-xxx が見つかりません"
}
```

- **422 Unprocessable Entity:** 最適化失敗（制約が厳しすぎる）
```json
{
  "detail": "最適化に失敗しました: VRP求解に失敗しました。制約が厳しすぎる可能性があります。"
}
```

- **500 Internal Server Error:** 予期しないエラー

---

## 🧪 テスト方法

### 1. サーバー起動

```bash
cd backend
python app/main.py
```

または

```bash
cd backend
uvicorn app.main:app --reload
```

**起動確認:**
- ブラウザで http://localhost:8000/docs にアクセス
- Swagger UI が表示されればOK

### 2. API自動テスト実行

```bash
cd backend
python scripts/test_api.py
```

**期待される出力:**
```
======================================================================
🚀 API エンドポイントテスト
======================================================================

📋 1. ヘルスチェック
GET /health
ステータスコード: 200
✅ 成功

📋 2. デモデータ作成
POST /api/v1/seed/demo-data
✅ 成功

...

✅ すべてのAPIテストが成功しました！
```

### 3. 手動テスト（curl）

**ステップ1: デモデータ作成**
```bash
curl -X POST http://localhost:8000/api/v1/seed/demo-data
```

**ステップ2: データ取得**
```bash
curl http://localhost:8000/api/v1/depots
curl http://localhost:8000/api/v1/vehicles
curl http://localhost:8000/api/v1/deliveries
```

**ステップ3: VRP最適化実行**
```bash
curl -X POST http://localhost:8000/api/v1/optimization/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "depot_ids": ["depot-tokyo"],
    "vehicle_ids": ["vehicle-001", "vehicle-002", "vehicle-003"],
    "delivery_ids": [
      "delivery-001", "delivery-002", "delivery-003", "delivery-004",
      "delivery-005", "delivery-006", "delivery-007", "delivery-008",
      "delivery-009", "delivery-010"
    ]
  }'
```

---

## 📊 性能指標

| 配送先数 | 拠点数 | 車両数 | 計算時間目標 | 上限 |
|---------|-------|-------|------------|------|
| 6点 | 1 | 2台 | 2-5秒 | 30秒 |
| 10点 | 1 | 3台 | 5-10秒 | 30秒 |
| 20点 | 1 | 3台 | 10-20秒 | 30秒 |
| **30点** | **2** | **5台** | **10-60秒** | **60秒** (Epic 005) |
| 50点 | 2 | 5台 | 30-60秒 | 60秒 |

---

## 🔒 エラーハンドリング

### 共通エラーコード

| ステータスコード | 意味 | 対処方法 |
|---------------|------|---------|
| 400 | Bad Request | リクエストパラメータを確認 |
| 404 | Not Found | 指定されたIDが存在するか確認 |
| 422 | Unprocessable Entity | 制約を緩和（車両数増加など） |
| 500 | Internal Server Error | ログを確認、開発者に連絡 |

### デバッグモード

`app/config.py` で `DEBUG: bool = True` に設定すると：
- SQLクエリがコンソールに出力される
- 詳細なエラーメッセージが表示される

---

## 📚 Swagger UI

FastAPI は自動的にインタラクティブなAPI ドキュメントを生成します。

**アクセス方法:**
1. サーバー起動: `python app/main.py`
2. ブラウザで http://localhost:8000/docs にアクセス
3. 各エンドポイントを展開してテスト実行可能

**主な機能:**
- ✅ リクエスト例の表示
- ✅ パラメータ説明
- ✅ レスポンススキーマ
- ✅ 「Try it out」ボタンで直接API実行

---

## 🚀 次のステップ

Task 5 完了後は：

1. **Task 6: 単元テスト** - pytest でテストカバレッジ 80% 以上
2. **Task 7: 統合テスト** - E2Eテスト（100配送点）
3. **フロントエンド統合** - React から API 呼び出し

---

## 💡 ベストプラクティス

### API設計

- ✅ **RESTful原則:** リソース指向のURL設計
- ✅ **明確なHTTPメソッド:** GET（読取）、POST（作成・実行）
- ✅ **適切なステータスコード:** 200, 201, 400, 404, 422, 500
- ✅ **詳細なエラーメッセージ:** 問題の特定と修正が容易

### データ検証

- ✅ **Pydantic スキーマ:** リクエスト/レスポンス自動検証
- ✅ **Repository パターン:** データアクセス層の分離
- ✅ **依存性注入:** `Depends(get_db)` で DB セッション管理

### セキュリティ

- ✅ **CORS設定:** フロントエンドからのアクセス制限
- ✅ **入力検証:** Pydantic によるスキーマ検証
- ⚠️ **認証・認可:** 本番環境では実装必須（Demo では省略）

---

## 🐛 既知の制限事項

1. **認証なし:** Demo プロトタイプのため認証機能なし
2. ~~**単一拠点のみ**~~ → ✅ **Epic 005で解決:** Multi-Depot VRP実装完了（2拠点対応）
   - `SetAllowedVehiclesForIndex`で拠点制約を実装
   - 各車両は所属拠点の配送先のみ訪問可能
3. ~~**重量容量制約のみ**~~ → ✅ **Epic 005で解決:** 双重容量制約実装（重量 + 容積）
   - `AddDimensionWithVehicleCapacity`で両方の制約を実装
   - 車両ごとに重量と容積の上限を独立管理
4. **基線統計の簡略化:** 未使用車両を0%積載率として平均計算
   - 改善指標（utilization_improvement_percent）に影響
   - Demo では最適化効果がやや過大評価される可能性あり
5. **同期API:** 長時間計算もブロッキング（60秒上限、Epic 005で延長）
6. **SQLite:** 本番環境では PostgreSQL 推奨
7. **単一アルゴリズム:** OR-Tools CVRPTW のみ
8. **固定配送点:** 配送点が`seed.py`にハードコード（国際化困難）
