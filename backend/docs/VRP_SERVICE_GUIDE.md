# VRP Service 開発ガイド

## 📁 ファイル構成

```
backend/app/services/
├── __init__.py                    # Service層エクスポート
├── baseline_service.py            # 基線計算サービス
├── metrics_service.py             # 改善指標計算サービス
└── vrp_service.py                 # VRP最適化サービス（⭐ 核心）
```

---

## 🎯 アーキテクチャ概要

### Service層の責務

```
Controller (API)
    ↓
Service Layer (ビジネスロジック)
    ├── VRPService ← OR-Tools最適化
    ├── BaselineService ← 基線計算
    └── MetricsService ← 改善指標計算
    ↓
Repository Layer (データアクセス)
```

---

## 🔧 BaselineService

**目的:** 最適化前の基準値（ベースライン）を計算

### アルゴリズム: Simple Assignment

```
1. 配送先を車両数で均等分割
2. 各車両が「拠点→配送先1→配送先2→...→拠点」の順で巡回
3. 総距離・総時間・総コストを計算
```

### 使い方

```python
from app.services.baseline_service import BaselineService

baseline_service = BaselineService()

# Haversine距離計算
distance_km = baseline_service.calculate_haversine_distance(
    lat1=35.6812, lon1=139.7671,  # 東京駅
    lat2=35.6895, lon2=139.6917   # 新宿駅
)
# => 約7.2km

# 基線メトリクス計算
baseline = baseline_service.calculate_simple_assignment(
    depots=[depot],
    vehicles=[vehicle1, vehicle2],
    deliveries=[delivery1, delivery2, delivery3]
)
# => {
#     "total_distance": 250.5,
#     "total_duration": 480,
#     "total_cost": 35000.0,
#     "average_utilization_weight": 65.3,
#     "method": "simple_assignment"
# }
```

### 主要メソッド

| メソッド | 説明 | 戻り値 |
|---------|------|--------|
| `calculate_haversine_distance(lat1, lon1, lat2, lon2)` | 2地点間の距離計算 | `float` (km) |
| `calculate_simple_assignment(depots, vehicles, deliveries)` | 基線メトリクス計算 | `Dict[str, Any]` |

---

## 📊 MetricsService

**目的:** 最適化による改善効果を定量化

### 計算内容

- **距離削減:** 基線 - 最適化後（km・%）
- **時間削減:** 基線 - 最適化後（分）
- **コスト削減:** 基線 - 最適化後（¥・%）
- **積載率改善:** 最適化後 - 基線（%）

### 使い方

```python
from app.services.metrics_service import MetricsService

metrics_service = MetricsService()

# 改善指標計算
improvement = metrics_service.calculate_improvement_metrics(
    baseline={
        "total_distance": 250.5,
        "total_duration": 480,
        "total_cost": 35000.0,
        "average_utilization_weight": 65.3
    },
    optimized_routes=[route1, route2]  # List[Route]
)
# => {
#     "distance_reduction_km": 50.2,
#     "distance_reduction_percent": 25.1,
#     "duration_reduction_minutes": 90,
#     "cost_reduction_amount": 8000.0,
#     "cost_reduction_percent": 22.8,
#     "utilization_improvement_percent": 12.5
# }

# ルート統計情報
stats = metrics_service.calculate_route_statistics(routes)
# => {
#     "total_routes": 10,
#     "total_stops": 100,
#     "avg_stops_per_route": 10.0,
#     "avg_distance_per_route": 45.8,
#     "avg_utilization_weight": 72.5,
#     "avg_utilization_volume": 68.3
# }
```

---

## 🚀 VRPService（核心）

**目的:** OR-Toolsを使用してCVRPTW（容量制約付き時間窓VRP）を解く

### アルゴリズム: OR-Tools CVRPTW

**制約:**
- ✅ 容量制約（重量）
- ✅ 時間窓制約（morning/afternoon）
- ✅ 各配送先は1度だけ訪問

**目標:**
- 🎯 総走行距離の最小化

**探索戦略:**
- **初期解:** PATH_CHEAPEST_ARC（最も安い辺を優先）
- **局所探索:** GUIDED_LOCAL_SEARCH（ガイド付き局所探索）
- **時間制限:** 10秒（設定可能）

### 使い方

```python
from app.services.vrp_service import VRPService

vrp_service = VRPService()

# VRP最適化実行
result = vrp_service.optimize(
    depots=[depot],
    vehicles=[vehicle1, vehicle2, vehicle3],
    deliveries=[delivery1, delivery2, ..., delivery100]
)

# 結果（OptimizationResult）
print(f"計算時間: {result.computation_time}ms")
print(f"ルート数: {len(result.routes)}")
print(f"総距離: {result.total_distance}km")
print(f"距離削減率: {result.improvement_metrics.distance_reduction_percent}%")
```

### データフロー

```
1. データモデル作成
   ├── 距離マトリクス生成（Haversine）
   ├── 時間マトリクス生成（距離÷速度）
   ├── 需要配列（重量）
   └── 時間窓配列

2. OR-Toolsモデル構築
   ├── RoutingIndexManager作成
   ├── RoutingModel作成
   ├── 距離コールバック登録
   ├── 容量制約追加
   └── 時間制約追加

3. 求解実行
   └── SolveWithParameters()

4. ルート抽出
   ├── 各車両のルートを走査
   ├── RouteStop作成（到着時刻・距離など）
   └── Route作成

5. メトリクス計算
   ├── 基線計算（BaselineService）
   └── 改善指標計算（MetricsService）

6. OptimizationResult返却
```

### 主要メソッド

| メソッド | 説明 | 戻り値 |
|---------|------|--------|
| `optimize(depots, vehicles, deliveries)` | VRP最適化実行 | `OptimizationResult` |
| `calculate_haversine_distance(...)` | Haversine距離計算 | `float` (km) |
| `_create_distance_matrix(...)` | 距離マトリクス作成 | `List[List[int]]` (m) |
| `_create_time_matrix(...)` | 時間マトリクス作成 | `List[List[int]]` (分) |
| `_create_data_model(...)` | OR-Tools用データ作成 | `Dict[str, Any]` |
| `_extract_routes(...)` | 解からルート抽出 | `List[Route]` |

---

## 🧪 テスト方法

### 基本テスト実行

```bash
cd backend
python scripts/test_vrp_service.py
```

**期待される出力:**

```
======================================================================
🚀 VRP最適化サービス テスト
======================================================================

📊 テストデータ作成中...
   拠点: 1箇所
   車両: 2台
   配送先: 6箇所
      - 午前指定: 3箇所
      - 午後指定: 2箇所
      - 時間指定なし: 1箇所

🔧 VRP最適化実行中...
   アルゴリズム: OR-Tools CVRPTW
   初期解戦略: PATH_CHEAPEST_ARC
   局所探索: GUIDED_LOCAL_SEARCH
   時間制限: 10秒

======================================================================
✅ 最適化成功！
======================================================================

📊 最適化結果:
   結果ID: ...
   計算時間: 342ms
   生成ルート数: 2
   未割当配送先: 0件

📈 パフォーマンス指標:
   総走行距離: 45.23 km
   総所要時間: 180 分
   総コスト: ¥8,261.50
   平均重量積載率: 38.50%
   平均容積積載率: 31.25%

📉 基線メトリクス（最適化前）:
   総走行距離: 52.15 km
   総所要時間: 195 分
   総コスト: ¥9,107.50
   平均積載率: 39.00%
   計算方法: simple_assignment

🎯 改善効果:
   距離削減: 6.92 km (13.3%)
   時間削減: 15 分
   コスト削減: ¥846.00 (9.3%)
   積載率改善: -0.50%

🚛 ルート詳細:
   ...

======================================================================
✅ すべてのテストが成功しました！
======================================================================
```

### 性能検証

**100配送点の場合:**
- ⏱️ 計算時間目標: 2-5秒
- 🔺 上限: 10秒
- 💾 メモリ使用: <1GB

---

## ⚙️ 設定

### config.py

```python
# VRP最適化設定
VRP_TIME_LIMIT_SECONDS: int = 10  # 最適化計算の最大時間（秒）
VRP_SOLUTION_LIMIT: int = 1000    # 解探索の最大数
```

### カスタマイズポイント

#### 1. 平均速度変更

```python
# vrp_service.py
class VRPService:
    AVERAGE_SPEED_KM_H = 30.0  # ← ここを変更
```

#### 2. 時間窓の定義変更

```python
# _create_data_model() 内
if delivery.time_window == "morning":
    time_windows.append((480, 720))  # 8:00-12:00
elif delivery.time_window == "afternoon":
    time_windows.append((780, 1080))  # 13:00-18:00
```

#### 3. 探索戦略変更

```python
# optimize() 内
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC  # ← 変更
)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH  # ← 変更
)
```

---

## 🐛 トラブルシューティング

### Error: "VRP求解に失敗しました"

**原因:**
- 制約が厳しすぎて実行可能解が存在しない
- 車両容量が不足
- 時間窓が矛盾

**対策:**
1. 制約を緩和（時間窓の幅を広げる）
2. 車両数を増やす
3. 配送先を減らす
4. `time_limit.seconds` を延長

### 計算時間が10秒を超える

**対策:**
1. `VRP_TIME_LIMIT_SECONDS` を調整
2. 探索戦略を変更（AUTOMATIC → PATH_CHEAPEST_ARC）
3. データ規模を確認（100点以下推奨）

### 改善率が低い（<20%）

**原因:**
- 基線計算（simple_assignment）がすでに良い解
- 配送先が密集している

**対策:**
- 正常動作（基線が良い場合は改善率が低くなる）
- デモ用に配送先を分散させる

---

## 📚 参考資料

### OR-Tools公式ドキュメント

- [VRP Guide](https://developers.google.com/optimization/routing)
- [CVRPTW Example](https://developers.google.com/optimization/routing/cvrptw)
- [Routing Options](https://developers.google.com/optimization/routing/routing_options)

### アルゴリズム詳細

- **Haversine Formula:** [Wikipedia](https://en.wikipedia.org/wiki/Haversine_formula)
- **Guided Local Search:** [OR-Tools Docs](https://developers.google.com/optimization/routing/local_search)
- **PATH_CHEAPEST_ARC:** 最も安い辺を優先的に選択する貪欲法

---

## 🚀 次のステップ

VRP Service が完成したら、次は：

1. **Task 5: API端点実装** - FastAPIエンドポイント作成
2. **Task 6: 単元テスト** - pytest でテストカバレッジ 80% 以上
3. **Task 7: 統合テスト** - E2Eテスト（100配送点）

---

## 📝 コーディング規約遵守確認

- ✅ **KISS:** 複雑なロジックを3つのServiceに分離
- ✅ **DRY:** Haversine計算を共通メソッド化
- ✅ **SOLID S:** 各Serviceは単一責務
- ✅ **SOLID O:** 拡張可能（探索戦略変更など）
- ✅ **Docstring:** すべてのpublicメソッドに記述
- ✅ **Type Hints:** 完全なtype annotation
