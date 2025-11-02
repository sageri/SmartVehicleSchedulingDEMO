# Repository層 開発ガイド

## 📁 ファイル構成

```
backend/app/repositories/
├── __init__.py                   # Repositoryエクスポート
├── base.py                       # 基底Repositoryクラス（Generic型）
├── depot_repository.py           # 拠点Repository
├── vehicle_repository.py         # 車両Repository
└── delivery_repository.py        # 配送先Repository
```

## 🎯 設計パターン

**Repository Pattern** を採用：
- データアクセスロジックをビジネスロジックから分離
- Generic型を使用してDRY原則を適用
- SQLAlchemyのクエリをカプセル化

## 🔧 基本的な使い方

### 1. Repositoryのインスタンス化

```python
from sqlalchemy.orm import Session
from app.repositories import DepotRepository, VehicleRepository, DeliveryRepository

# セッション取得
db: Session = ...

# Repositoryインスタンス作成
depot_repo = DepotRepository(db)
vehicle_repo = VehicleRepository(db)
delivery_repo = DeliveryRepository(db)
```

### 2. CRUD操作

```python
# Create（作成）
depot = Depot(id="depot-001", name="東京デポ", ...)
created_depot = depot_repo.create(depot)

# Read（読取）
depot = depot_repo.get_by_id("depot-001")
all_depots = depot_repo.get_all()

# Update（更新）
depot.name = "新東京デポ"
updated_depot = depot_repo.update(depot)

# Delete（削除）
deleted = depot_repo.delete("depot-001")

# Count（カウント）
count = depot_repo.count()

# Exists（存在確認）
exists = depot_repo.exists("depot-001")
```

### 3. カスタム検索メソッド

#### DepotRepository

```python
# 拠点名で検索
depot = depot_repo.get_by_name("東京デポ")

# 複数IDで一括取得
depots = depot_repo.get_by_ids(["depot-001", "depot-002"])

# 位置範囲で検索
depots = depot_repo.search_by_location(
    min_lat=35.0, max_lat=36.0,
    min_lon=139.0, max_lon=140.0
)
```

#### VehicleRepository

```python
# 拠点IDで検索
vehicles = vehicle_repo.get_by_depot("depot-001")

# 車両タイプで検索
vehicles = vehicle_repo.get_by_type("2t")

# 拠点IDとタイプで検索
vehicles = vehicle_repo.get_by_depot_and_type("depot-001", "2t")

# 拠点の車両数をカウント
count = vehicle_repo.count_by_depot("depot-001")
```

#### DeliveryRepository

```python
# 時間窓で検索
morning_deliveries = delivery_repo.get_by_time_window("morning")
afternoon_deliveries = delivery_repo.get_by_time_window("afternoon")
anytime_deliveries = delivery_repo.get_by_time_window(None)

# 顧客名で部分一致検索
deliveries = delivery_repo.search_by_customer_name("山田")

# 重量範囲で検索
deliveries = delivery_repo.get_by_weight_range(100.0, 200.0)

# 統計情報取得
stats = delivery_repo.get_statistics()
# => {
#     "total": 100,
#     "morning": 30,
#     "afternoon": 70,
#     "anytime": 0,
#     "avg_weight": 125.5,
#     "total_weight": 12550.0
# }
```

## 🧪 テスト方法

### 単体テスト実行

```bash
cd backend
python scripts/test_repositories.py
```

**期待される出力:**

```
🚀 Repository層テストを開始します...

============================================================
📍 Depot Repository テスト
============================================================
✅ Create: テストデポ (ID: depot-test-001)
✅ Read by ID: テストデポ
✅ Count: 1 depots
✅ Get All: 1 depots

============================================================
🚚 Vehicle Repository テスト
============================================================
✅ Create: 2t (ID: vehicle-test-001)
✅ Get by Depot: 1 vehicles
✅ Get by Type (2t): 1 vehicles
✅ Count by Depot: 1 vehicles

============================================================
📦 Delivery Repository テスト
============================================================
✅ Create (Morning): 山田商店
✅ Create (Afternoon): 佐藤商店
✅ Get by Time Window (morning): 1 deliveries
✅ Get by Time Window (afternoon): 1 deliveries
✅ Search by Customer Name ('山田'): 1 results
✅ Statistics:
   - Total: 2
   - Morning: 1
   - Afternoon: 1
   - Average Weight: 115.00 kg
   - Total Weight: 230.00 kg

============================================================
🧹 Cleanup テスト
============================================================
✅ Delete delivery-test-001: True
✅ Delete vehicle-test-001: True
✅ Delete depot-test-001: True
✅ Verify deletion (should be False): False

============================================================
✅ すべてのテストが成功しました！
============================================================
```

## 📊 BaseRepository API

すべてのRepositoryが継承する基底クラスの共通メソッド：

| メソッド | 説明 | 戻り値 |
|---------|------|--------|
| `get_by_id(id)` | IDでレコード取得 | `Optional[ModelType]` |
| `get_all(skip, limit)` | 全レコード取得 | `List[ModelType]` |
| `count(filters)` | レコード数カウント | `int` |
| `create(obj)` | レコード作成 | `ModelType` |
| `update(obj)` | レコード更新 | `ModelType` |
| `delete(id)` | レコード削除 | `bool` |
| `delete_all()` | 全削除（⚠️危険） | `int` |
| `exists(id)` | 存在確認 | `bool` |

## 🔒 トランザクション管理

Repository層ではトランザクションを **明示的にコミット** します：

```python
# ❌ 誤った使い方（自動コミットされない）
depot_repo.create(depot)
# まだDBには反映されていない！

# ✅ 正しい使い方（Repositoryが内部でコミット）
created_depot = depot_repo.create(depot)
# DBに反映済み
```

複数操作のアトミック性が必要な場合：

```python
from app.database import SessionLocal

db = SessionLocal()
try:
    depot_repo = DepotRepository(db)
    vehicle_repo = VehicleRepository(db)

    # 手動トランザクション管理
    depot = depot_repo.create(depot_obj)
    vehicle = vehicle_repo.create(vehicle_obj)

    db.commit()  # 両方とも成功した場合のみコミット
except Exception as e:
    db.rollback()  # エラー時はロールバック
    raise
finally:
    db.close()
```

## 📝 コーディング規約

### 命名規則

- Repository クラス名: `{Model}Repository`（例: `DepotRepository`）
- カスタムメソッド名: `get_by_{field}`, `search_by_{field}`, `count_by_{field}`

### メソッドの戻り値

- **単一レコード**: `Optional[ModelType]` - 存在しない場合は `None`
- **複数レコード**: `List[ModelType]` - 0件の場合は空リスト `[]`
- **カウント**: `int` - 0件の場合は `0`
- **削除**: `bool` - 成功時 `True`、失敗時 `False`

### Docstring

すべてのメソッドに Google Style Docstring を記述：

```python
def get_by_depot(self, depot_id: str) -> List[Vehicle]:
    """
    拠点IDで車両を検索

    Args:
        depot_id: 拠点ID

    Returns:
        List[Vehicle]: 該当拠点の車両リスト
    """
    ...
```

## 🚀 次のステップ

Repository層が完成したら、次は：

1. **VRP Service 実装** - OR-Tools を使用した最適化エンジン
2. **API Endpoints 実装** - FastAPI ルーターで Repository を使用
3. **単体テスト** - pytest でテストカバレッジ 80% 以上を目指す

## 📚 参考

- [Repository Pattern - Microsoft Docs](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Generic Types in Python](https://docs.python.org/3/library/typing.html#typing.Generic)
