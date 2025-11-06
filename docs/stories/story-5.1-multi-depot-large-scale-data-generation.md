# Story 5.1: 多拠点・中規模配送先データ生成機能の実装

**Story Type:** Brownfield Enhancement
**Status:** ✅ 完了（2025-11-04）
**Created:** 2025-11-03
**Completed:** 2025-11-04
**Priority:** P1 (High)
**Epic:** [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
**Estimated Effort:** 3-4 hours
**Actual Effort:** ~5 hours

**スコープ変更履歴:**
- **2025-11-03 初期:** 4拠点・100件で計画 → 2拠点・40件に変更（パフォーマンス改善）
- **2025-11-03 Story 5.1実装:** 2拠点・40件実装完了（ランダム生成方式）
- **2025-11-04 Story 5.1.1拡張:** 30件に最適化（東京20+さいたま10）、固定配送点リスト方式採用

---

## 📋 User Story

**As a** システム管理者（Demo環境担当者）
**I want** 2拠点・30配送先・実在地点使用のDemoデータ生成機能
**So that** 中規模実証環境で現実的な物流シナリオをデモンストレーションできる

---

## 🎯 最終実装内容（Final Implementation）

### 実装概要

Story 5.1は当初「2拠点・40件のランダム生成」として実装されましたが、Story 5.1.1で以下の重要な改善を実施しました：

1. **固定配送点リスト方式への移行**
   - ランダム生成 → 実在地点30箇所の固定リスト
   - 海上配置問題の完全解消
   - デモ説得力の向上

2. **配送点分布の最適化**
   - 総数: 40件 → **30件**
   - 分布: 各拠点20件 → **東京20件 + さいたま市10件**

3. **拠点変更**
   - 拠点2: 横浜デポ → **さいたま市デポ**（より内陸で適切）

### 最終データ仕様

**拠点構成（2拠点）:**
```yaml
拠点1: 東京デポ
  ID: depot-tokyo
  座標: 35.6812, 139.7671
  住所: 東京都千代田区丸の内1-1-1
  営業時間: 8:00-18:00
  配送先: 20件（実在地点）
  車両: 3台（2t×2、4t×1）

拠点2: さいたま市デポ
  ID: depot-saitama
  座標: 35.8617, 139.6455
  住所: 埼玉県さいたま市大宮区桜木町1-1-1
  営業時間: 8:00-18:00
  配送先: 10件（実在地点）
  車両: 2台（2t×2）
```

**配送先構成（30件）:**
```yaml
東京デポ周辺（20件）:
  - 新宿区役所、渋谷駅周辺、池袋サンシャインシティ
  - 上野駅周辺、東京駅周辺、品川駅周辺
  - 目黒駅周辺、五反田駅周辺、中野駅周辺
  - 吉祥寺駅周辺、立川駅周辺、八王子駅周辺
  - 町田駅周辺、秋葉原駅周辺、錦糸町駅周辺
  - 北千住駅周辺、赤羽駅周辺、国分寺市役所
  - 小平市役所、府中市役所

さいたま市デポ周辺（10件）:
  - さいたま新都心、浦和駅周辺、大宮駅周辺
  - 川越市役所、所沢駅周辺、春日部駅周辺
  - 越谷市役所、草加駅周辺、熊谷駅周辺
  - 川口駅周辺
```

**伝票枚数分布（重み付きランダム）:**
```yaml
1枚: 50%（軽量・小型荷物）
2枚: 35%（標準荷物）
3枚: 15%（大型荷物）
```

**時間指定分布（最終調整版）:**
```yaml
午前指定（morning）: 20%（8:00-13:00）
午後指定（afternoon）: 30%（12:00-18:00）
時間指定なし（None）: 50%（8:00-18:00）- VRP解探索性向上のため大幅増加
```

---

## ✅ 達成基準（最終版）

### Functional Requirements（最終実装基準）

1. **2拠点の正確な生成** ✅
   - 東京デポ: `35.6812, 139.7671`
   - さいたま市デポ: `35.8617, 139.6455`
   - 各拠点の営業時間: 8:00-18:00
   - 拠点ID: `depot-tokyo`, `depot-saitama`

2. **30件配送先の生成（固定リスト方式）** ✅
   - 東京周辺: **20件**（実在地点）
   - さいたま市周辺: **10件**（実在地点）
   - 全配送点が陸地上
   - `FIXED_DELIVERY_LOCATIONS` 辞書定義

3. **伝票枚数の変動対応** ✅
   - 1枚: **50%** の確率
   - 2枚: **35%** の確率
   - 3枚: **15%** の確率
   - 各配送先の `weight` と `volume` を伝票枚数に比例

4. **時間指定3種類対応（最適化版）** ✅
   - 午前指定: **20%**（従来30%から削減）
   - 午後指定: **30%**（従来60%から削減）
   - 時間指定なし: **50%**（従来10%から大幅増加）

### Integration Requirements

5. **既存API維持** ✅
   - `/api/v1/seed/demo-data` エンドポイント維持
   - HTTPメソッド、URL、レスポンス形式は不変

6. **データモデル拡張** ✅
   - `Delivery.depot_id` フィールド追加（ForeignKey）
   - 既存スキーマへの後方互換性考慮（SQLite再作成）

7. **Multi-Depot VRP統合** ✅
   - 2拠点から独立したルート生成成功
   - 拠点制約実装（SetAllowedVehiclesForIndex）
   - 各拠点から安定的にルート生成

### Quality Requirements

8. **データバリデーション** ✅
   - 全配送点が陸地上（海上配置0件）
   - 実在地点30箇所の手動検証完了
   - 伝票枚数分布が仕様通り
   - 時間指定割合が最適化仕様通り

9. **既存機能の回帰テスト** ✅
   - Story 001-004の機能が正常動作
   - VRP最適化が30件データで正常動作（10-60秒）

10. **ドキュメント更新** ✅
    - Epic 005ドキュメント更新完了
    - Story 5.1.1完成報告作成完了

---

## 📊 最終実装との差異

### 当初計画 vs 最終実装

| 項目 | 当初計画 | 最終実装 | 変更理由 |
|------|----------|----------|----------|
| **配送点生成方式** | ランダム生成（bearing制約付き） | 固定配送点リスト | 海上配置問題の完全解消 |
| **配送点数** | 40件（各拠点20件） | 30件（東京20+さいたま10） | パフォーマンス最適化 |
| **拠点2** | 横浜デポ | さいたま市デポ | より内陸で適切 |
| **時間指定分布** | 午前30%/午後60%/指定なし10% | 午前20%/午後30%/指定なし50% | VRP解探索性向上 |
| **データモデル** | 変更なし | `Delivery.depot_id`追加 | 拠点制約実装のため |

### 主要な追加実装（Story 5.1.1）

以下の機能はStory 5.1.1で追加実装されました：

1. **固定配送点リスト（`FIXED_DELIVERY_LOCATIONS`）**
   ```python
   FIXED_DELIVERY_LOCATIONS = {
       "depot-tokyo": [
           {"name": "新宿区役所", "latitude": 35.6938, "longitude": 139.7034},
           # ... 全20件
       ],
       "depot-saitama": [
           {"name": "さいたま新都心", "latitude": 35.8944, "longitude": 139.6306},
           # ... 全10件
       ],
   }
   ```

2. **拠点別配送点数設定（辞書化）**
   ```python
   DELIVERIES_PER_DEPOT = {
       "depot-tokyo": 20,
       "depot-saitama": 10,
   }
   ```

3. **`Delivery.depot_id`フィールド**
   - データモデル拡張（ForeignKey）
   - 拠点-配送先の明確な関連付け

4. **VRP拠点制約**
   - `SetAllowedVehiclesForIndex`実装
   - 各車両が所属拠点の配送先のみ訪問

5. **VRP性能最適化**
   - タイムアウト300秒→60秒
   - 初期解戦略変更（PARALLEL_CHEAPEST_INSERTION）
   - 時間窓最適化（重複期間設定）

**詳細は以下を参照:**
- [Story 5.1.1 完成報告](story-5.1.1-completion-report.md)

---

## 🛠️ Technical Notes（参考：初期計画の技術アプローチ）

**注意:** 以下は初期計画時の技術実装案です。最終実装は固定配送点リスト方式を採用したため、ランダム生成関連のロジックは簡略化されています。

### Integration Approach（初期計画）

1. **`create_demo_data()` 関数の拡張**
   - 既存の関数シグネチャを維持
   - 内部ロジックを拡張（2拠点 + 30配送先対応）
   - エラーハンドリングを強化

2. **地理的分布アルゴリズム（初期計画、最終的には固定リスト採用）**

   **最終実装では以下のアプローチを使用:**
   - 固定配送点リストからの順次取得
   - ランダム生成ロジックは削除
   - 伝票枚数と時間指定のみランダム

---

## 🎯 Definition of Done（最終版）

- [x] **2拠点が仕様通りの座標で生成される**
  - 東京デポ: ✅ 完了
  - さいたま市デポ: ✅ 完了

- [x] **30件の配送先が実在地点で生成される**
  - 東京20件: ✅ 完了（実在地点）
  - さいたま10件: ✅ 完了（実在地点）
  - 海上配置: ✅ 0件（完全解消）

- [x] **伝票枚数が重み付きランダム（50%/35%/15%）で分布する**

- [x] **時間指定が最適化仕様（20%/30%/50%）で分布する**

- [x] **データバリデーション関数が正常動作する**

- [x] **既存の `/api/v1/seed/demo-data` APIエンドポイントが動作する**

- [x] **VRP最適化が30件のデータに対して動作する**
  - 計算時間: ✅ 10-60秒（目標達成）
  - Multi-Depotルート: ✅ 東京+さいたま両方生成
  - 拠点制約: ✅ 正常動作

- [x] **既存機能（Story 001-004）の回帰テストが成功する**

- [x] **ドキュメント更新完了**
  - Epic 005: ✅ 更新完了
  - Story 5.1.1完成報告: ✅ 作成完了
  - Story 5.1（本文書）: ✅ 更新完了

- [x] **コードが既存のパターンとスタイルに準拠している**

---

## ⚠️ Risk and Compatibility Check

### Primary Risk（解決済み）

**Risk:** ランダム生成で地理的に偏った配置（特に海上配置）が発生する

**実施した対策:**
- ✅ 固定配送点リスト方式を採用
- ✅ 実在地点30箇所を手動検証
- ✅ 海上配置問題完全解消

**結果:**
- ✅ 海上配置0件達成
- ✅ 再現性向上（毎回同じデータ）
- ✅ デモ説得力向上

### Compatibility Verification

- [x] **No breaking changes to existing APIs** ✅
  → `/api/v1/seed/demo-data` のインターフェースは不変

- [x] **Database changes are documented** ✅
  → `Delivery.depot_id`追加、SQLite再作成で対応

- [x] **UI changes follow existing design patterns** ✅
  → 拠点カラーマッピング更新（横浜→さいたま市）

- [x] **Performance impact is positive** ✅
  → VRP計算時間が300秒→10-60秒に大幅改善

---

## 📚 Related Documents

- [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
- [Story 5.1.1: データ生成最適化と拠点制約実装 - 完成報告](story-5.1.1-completion-report.md)（**重要：最終実装の詳細**）
- [Story 5.1.1: 初期計画ドキュメント](story-5.1.1-data-generation-land-constraint-optimization.md)
- [Story 5.2: 大規模車両管理機能の実装](story-5.2-large-scale-vehicle-management.md)
- [Story 5.3: UI/UX調整とパフォーマンス検証](story-5.3-ui-ux-performance-optimization.md)

---

## 📝 Implementation Summary

### 実装完了内容

✅ **Phase 1: 拠点生成（2025-11-03）**
- 2拠点の座標定義と生成ロジック実装
- 初期は横浜デポ、後にさいたま市デポに変更

✅ **Phase 2: 配送先生成（2025-11-03 → 2025-11-04）**
- 初期：ランダム生成方式（40件）
- 最終：固定配送点リスト方式（30件）

✅ **Phase 3: 伝票枚数・時間指定分布（2025-11-03 → 2025-11-04）**
- 重み付きランダム実装
- 時間指定分布最適化（10%→50%柔軟性向上）

✅ **Phase 4: バリデーションとテスト（2025-11-04）**
- データバリデーション関数実装
- 海上配置検証（0件達成）
- VRP最適化統合テスト成功

✅ **Phase 5: ドキュメント更新（2025-11-04）**
- Epic 005更新
- Story 5.1.1完成報告作成
- 本ドキュメント更新

### 主要成果

| 指標 | 成果 |
|------|------|
| **海上配置問題** | ✅ 100%解消 |
| **配送先数** | ✅ 30件（最適化） |
| **VRP計算時間** | ✅ 10-60秒（5倍高速化） |
| **Multi-Depotルート** | ✅ 安定生成 |
| **拠点制約** | ✅ 実装完了 |

---

## 🎬 Next Steps After Completion

✅ **完了済み:**
1. Story 5.1.1 - データ生成最適化と拠点制約実装
2. Story 5.2 - Multi-Depot VRP実装
3. Story 5.3 - UI/UX調整とパフォーマンス検証

**Epic 005 完了（2025-11-04）**

---

**🤖 Generated by PM Agent (John)**
**📅 Created:** 2025-11-03
**📅 Last Updated:** 2025-11-04
**📊 Status:** ✅ 完了
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

- [x] **2拠点が仕様通りの座標で生成される**
  - 東京デポ: ✅ 完了
  - さいたま市デポ: ✅ 完了

- [x] **30件の配送先が実在地点で生成される**
  - 東京20件: ✅ 完了（実在地点）
  - さいたま市10件: ✅ 完了（実在地点）
  - 海上配置: ✅ 0件（完全解消）

- [x] **伝票枚数が重み付きランダム（50%/35%/15%）で分布する**

- [x] **時間指定が最適化仕様（20%/30%/50%）で分布する**

- [x] **VRP最適化が30件のデータに対して動作する**
  - 計算時間: ✅ 10-60秒（目標達成）
  - Multi-Depotルート: ✅ 東京+さいたま両方生成
  - 拠点制約: ✅ 正常動作

- [x] **既存機能（Story 001-004）の回帰テストが成功する**

- [x] **ドキュメント更新完了**

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
