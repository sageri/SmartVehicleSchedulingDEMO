# Story 5.1: 多拠点・大規模配送先データ生成機能の実装

**Story Type:** Brownfield Enhancement
**Status:** 📝 To Do
**Created:** 2025-11-03
**Priority:** P1 (High)
**Epic:** [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
**Estimated Effort:** 4-6 hours

---

## 📋 User Story

**As a** システム管理者（Demo環境担当者）
**I want** 4拠点・100配送先・伝票枚数変動対応のDemoデータ生成機能
**So that** 大規模実証環境で現実的な物流シナリオをデモンストレーションできる

---

## 🎯 Story Context

### Existing System Integration

**Integrates with:**
- `/api/v1/seed/demo-data` エンドポイント（既存）
- `backend/app/api/v1/seed.py` のデータ生成ロジック
- `backend/app/repositories/*.py` のRepository層

**Technology:**
- FastAPI + SQLAlchemy
- Python 3.12+
- PostgreSQL (dev: SQLite)

**Follows pattern:**
- 既存の `create_demo_data()` 関数パターンを踏襲
- Repository パターンで DB アクセス
- トランザクション管理は既存実装を維持

**Touch points:**
- `DepotRepository.create()` - 拠点生成
- `DeliveryRepository.create()` - 配送先生成
- Database models: `Depot`, `Delivery`

---

## ✅ Acceptance Criteria

### Functional Requirements

1. **4拠点の正確な生成**
   - 東京デポ（自拠点）: `35.6812, 139.7671`
   - 横浜デポ: `35.4657, 139.6220`（南方向約15km）
   - 川口デポ: `35.8078, 139.7242`（北方向約10km）
   - 市川デポ: `35.7226, 139.9306`（東方向約12km）
   - 各拠点の営業時間: 8:00-18:00
   - 各拠点に `depot_id` を付与（例: `depot-tokyo`, `depot-yokohama`）

2. **100件配送先の生成（エリア分割方式）**
   - 各拠点周辺に **25件** ずつ配置（計100件）
   - 各拠点から半径 **50km圏内** にランダム配置
   - 緯度・経度の正確な計算（Haversine距離）
   - 地理的偏りを避けるための分布検証

3. **伝票枚数の変動対応（重み付きランダム）**
   - 1枚: **50%** の確率（軽量・小型荷物）
   - 2枚: **35%** の確率（標準荷物）
   - 3枚: **15%** の確率（大型荷物）
   - 各配送先の `weight` と `volume` を伝票枚数に比例して設定

4. **時間指定3種類対応**
   - 午前指定（`morning`）: **30%**
   - 午後指定（`afternoon`）: **60%**
   - 時間指定なし（`None`）: **10%**
   - 各エリアで割合を維持

### Integration Requirements

5. **既存の `/api/v1/seed/demo-data` APIエンドポイント維持**
   - HTTPメソッド、URL、レスポンス形式は不変
   - 既存のクライアント（Frontend）への互換性保証

6. **既存のデータモデルパターン踏襲**
   - `Depot` モデルのスキーマ不変
   - `Delivery` モデルのスキーマ不変
   - 既存のバリデーションルールを尊重

7. **トランザクション管理の一貫性**
   - 既存の `session.begin()` / `session.commit()` パターン維持
   - エラー時のロールバック処理を実装
   - データ生成失敗時は全データをクリア

### Quality Requirements

8. **データバリデーション**
   - 全拠点が半径20km圏内に配置されることを検証
   - 全配送先が各拠点から半径50km圏内に配置されることを検証
   - 伝票枚数分布が仕様通り（50%/35%/15%）に近いことを検証
   - 時間指定割合が仕様通り（30%/60%/10%）に近いことを検証

9. **既存機能の回帰テスト**
   - Story 001-004 の機能が正常動作することを確認
   - VRP最適化が100件のデータに対して動作することを確認

10. **ドキュメント更新**
    - `README.md` の「Demoデータ仕様」セクションを更新
    - API仕様書（必要に応じて）を更新

---

## 🛠️ Technical Notes

### Integration Approach

1. **`create_demo_data()` 関数の拡張**
   - 既存の関数シグネチャを維持
   - 内部ロジックを拡張（4拠点 + 100配送先対応）
   - エラーハンドリングを強化

2. **地理的分布アルゴリズム**
   ```python
   # エリア分割方式の実装例
   def generate_deliveries_around_depot(
       depot: Depot,
       count: int,
       max_radius_km: float,
       time_window_distribution: dict
   ) -> List[Delivery]:
       """
       指定した拠点の周辺にランダムに配送先を生成

       Args:
           depot: 中心となる拠点
           count: 生成する配送先数（例: 25件）
           max_radius_km: 最大半径（例: 50km）
           time_window_distribution: 時間指定割合（例: {'morning': 0.3, 'afternoon': 0.6, None: 0.1}）

       Returns:
           List[Delivery]: 生成された配送先リスト
       """
       deliveries = []
       for i in range(count):
           # ランダムな距離と角度を生成
           distance = random.uniform(0, max_radius_km)
           angle = random.uniform(0, 2 * math.pi)

           # 緯度・経度を計算（Haversine逆変換）
           lat, lon = calculate_destination_point(depot.latitude, depot.longitude, distance, angle)

           # 伝票枚数を重み付きランダムで決定
           num_packages = random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]

           # 時間指定を分布に従って決定
           time_window = random.choices(
               ['morning', 'afternoon', None],
               weights=[0.3, 0.6, 0.1]
           )[0]

           deliveries.append(Delivery(
               id=f"delivery-{depot.id}-{i+1}",
               latitude=lat,
               longitude=lon,
               weight=10.0 * num_packages,  # 1伝票あたり10kg
               volume=0.5 * num_packages,   # 1伝票あたり0.5m³
               time_window=time_window,
               service_time=15,  # 15分固定
               priority=1,
               depot_id=depot.id
           ))

       return deliveries
   ```

2. **Haversine逆変換関数（目的地座標計算）**
   ```python
   def calculate_destination_point(
       lat: float, lon: float, distance_km: float, bearing_rad: float
   ) -> Tuple[float, float]:
       """
       Haversine逆変換: 出発点・距離・方位から目的地座標を計算

       Args:
           lat: 出発点の緯度（度）
           lon: 出発点の経度（度）
           distance_km: 移動距離（km）
           bearing_rad: 方位角（ラジアン、0=北）

       Returns:
           Tuple[float, float]: 目的地の(緯度, 経度)

       Reference:
           https://www.movable-type.co.uk/scripts/latlong.html
       """
       import math

       EARTH_RADIUS_KM = 6371.0
       lat_rad = math.radians(lat)
       lon_rad = math.radians(lon)

       angular_distance = distance_km / EARTH_RADIUS_KM

       dest_lat_rad = math.asin(
           math.sin(lat_rad) * math.cos(angular_distance) +
           math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
       )

       dest_lon_rad = lon_rad + math.atan2(
           math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
           math.cos(angular_distance) - math.sin(lat_rad) * math.sin(dest_lat_rad)
       )

       return math.degrees(dest_lat_rad), math.degrees(dest_lon_rad)
   ```

3. **データバリデーション関数**
   ```python
   def validate_data_distribution(
       depots: List[Depot],
       deliveries: List[Delivery]
   ) -> Dict[str, Any]:
       """
       生成されたデータの分布を検証

       Returns:
           Dict: バリデーション結果
               - depot_distances_valid: bool
               - max_depot_distance_km: float
               - delivery_distances_valid: bool
               - package_distribution: dict
               - time_window_distribution: dict
       """
       # 1. 拠点間距離の検証（全て20km圏内か？）
       max_depot_distance = 0.0
       for i, depot_a in enumerate(depots):
           for depot_b in depots[i+1:]:
               dist = calculate_haversine_distance(
                   depot_a.latitude, depot_a.longitude,
                   depot_b.latitude, depot_b.longitude
               )
               max_depot_distance = max(max_depot_distance, dist)

       depot_distances_valid = max_depot_distance <= 20.0

       # 2. 配送先の分布検証（各拠点から50km圏内か？）
       delivery_distances_valid = True
       for delivery in deliveries:
           depot = next(d for d in depots if d.id == delivery.depot_id)
           dist = calculate_haversine_distance(
               depot.latitude, depot.longitude,
               delivery.latitude, delivery.longitude
           )
           if dist > 50.0:
               delivery_distances_valid = False
               break

       # 3. 伝票枚数分布の検証（50%/35%/15%に近いか？）
       package_counts = [
           int(d.weight / 10.0) for d in deliveries  # weight = 10kg * 伝票数
       ]
       package_distribution = {
           1: round(package_counts.count(1) / len(deliveries) * 100, 1),
           2: round(package_counts.count(2) / len(deliveries) * 100, 1),
           3: round(package_counts.count(3) / len(deliveries) * 100, 1),
       }

       # 4. 時間指定分布の検証（30%/60%/10%に近いか？）
       time_windows = [d.time_window for d in deliveries]
       time_window_distribution = {
           'morning': round(time_windows.count('morning') / len(deliveries) * 100, 1),
           'afternoon': round(time_windows.count('afternoon') / len(deliveries) * 100, 1),
           None: round(time_windows.count(None) / len(deliveries) * 100, 1),
       }

       return {
           "depot_distances_valid": depot_distances_valid,
           "max_depot_distance_km": round(max_depot_distance, 2),
           "delivery_distances_valid": delivery_distances_valid,
           "package_distribution": package_distribution,
           "time_window_distribution": time_window_distribution,
       }
   ```

4. **シード値固定オプションの追加**
   ```python
   def create_demo_data(seed: Optional[int] = 42) -> Dict[str, Any]:
       """
       Demoデータ生成

       Args:
           seed: ランダムシード値（再現可能なテスト用）。
                 デフォルト: 42（固定値で毎回同じデータ生成）
                 None の場合: 完全ランダム（毎回異なるデータ生成）

       Returns:
           Dict: 生成結果
               - depots: List[Depot]
               - vehicles: List[Vehicle]
               - deliveries: List[Delivery]
               - validation_result: Dict
       """
       import random

       # シード値を固定（テストやデバッグ時の再現性確保）
       if seed is not None:
           random.seed(seed)
           # これにより、同じseed値で毎回同じデータが生成される

       # ... データ生成ロジック
   ```

### Existing Pattern Reference

参考実装: `backend/app/api/v1/seed.py:84-348`

既存の `create_demo_data()` 関数は以下のパターンを使用：
- Repository パターンでの CRUD 操作
- トランザクション管理（`session.begin()` / `session.commit()`）
- エラー時のロールバック（`session.rollback()`）
- 固定座標での拠点生成
- ループでの配送先生成

**拡張方針:**
- 既存のパターンを維持しつつ、拠点数を4に拡張
- 配送先生成ロジックをエリア分割方式に変更
- 伝票枚数と時間指定の分布ロジックを追加

### Key Constraints

- **パフォーマンス:** データ生成は **30秒以内** に完了すること
- **メモリ:** 100件のデータ生成でメモリオーバーフローしないこと
- **精度:** 地理的分布の精度は **±1km** 程度の誤差を許容
- **互換性:** 既存の Frontend コードに変更を加えないこと

---

## 🎯 Definition of Done

- [x] 4拠点が仕様通りの座標で生成される
- [x] 100件の配送先が各拠点周辺25件ずつ生成される
- [x] 伝票枚数が重み付きランダム（50%/35%/15%）で分布する
- [x] 時間指定が仕様通り（30%/60%/10%）で分布する
- [x] データバリデーション関数が正常動作する
- [x] 既存の `/api/v1/seed/demo-data` APIエンドポイントが動作する
- [x] VRP最適化が100件のデータに対して動作する（Story 5.2完了後に確認）
- [x] 既存機能（Story 001-004）の回帰テストが成功する
- [x] `README.md` の Demoデータ仕様が更新される
- [x] コードが既存のパターンとスタイルに準拠している

---

## ⚠️ Risk and Compatibility Check

### Primary Risk

**Risk:** ランダム生成で地理的に偏った配置が発生する可能性

**Mitigation:**
- エリア分割方式を採用（各拠点周辺25件ずつ）
- 距離制約の検証関数を実装
- 生成後のバリデーションで分布を確認
- 必要に応じて再生成ロジックを追加

**Rollback:**
- データ生成は既存の `DELETE FROM` クエリで全削除可能
- 既存の20件データ生成ロジックはコメント保存
- 切り戻しは `/api/v1/seed/demo-data` の再実行で対応

### Compatibility Verification

- [x] **No breaking changes to existing APIs**
  → `/api/v1/seed/demo-data` のインターフェースは不変

- [x] **Database changes are additive only**
  → スキーマ変更なし（既存の `Depot` と `Delivery` テーブルを使用）

- [x] **UI changes follow existing design patterns**
  → Backend のみの変更、Frontend への影響なし（Story 5.3で対応）

- [x] **Performance impact is negligible**
  → データ生成は30秒以内、API レスポンスタイムへの影響なし

---

## 📚 Related Documents

- [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
- [Story 5.2: 大規模車両管理機能の実装](story-5.2-large-scale-vehicle-management.md)
- [Story 5.3: UI/UX調整とパフォーマンス検証](story-5.3-ui-ux-performance-optimization.md)

---

## 📝 Implementation Checklist

### Phase 1: 拠点生成ロジック拡張
- [ ] 4拠点の座標定義（定数またはコンフィグ）
- [ ] 拠点生成ループの実装
- [ ] 拠点間距離の検証関数実装

### Phase 2: 配送先生成ロジック拡張
- [ ] `generate_deliveries_around_depot()` 関数実装
- [ ] Haversine 逆変換（座標計算）関数実装
- [ ] エリア分割方式のループ実装

### Phase 3: 伝票枚数・時間指定分布
- [ ] 重み付きランダム（50%/35%/15%）実装
- [ ] 時間指定分布（30%/60%/10%）実装
- [ ] 分布検証関数実装

### Phase 4: バリデーションとテスト
- [ ] データバリデーション関数実装
- [ ] 単体テスト作成（`test_seed.py`）
- [ ] 統合テスト実行（APIエンドポイント経由）
- [ ] 既存機能の回帰テスト実行

### Phase 5: ドキュメント更新
- [ ] `README.md` の Demoデータ仕様セクション更新
- [ ] API仕様書更新（必要に応じて）
- [ ] 実装ノート作成（`docs/implementation-notes/`）

---

## 🎬 Next Steps After Completion

1. **Story 5.2 開始** - 大規模車両管理機能の実装
2. **統合テスト** - 100件データ + 10台車両でのVRP最適化検証
3. **Story 5.3 準備** - Frontend UI/UX調整の要件確認

---

**🤖 Generated by PM Agent (John)**
**📅 Last Updated:** 2025-11-03
