# Story 5.2: 大規模車両管理機能の実装

**Story Type:** Brownfield Enhancement
**Status:** 📝 To Do
**Created:** 2025-11-03
**Priority:** P1 (High)
**Epic:** [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
**Estimated Effort:** 2-3 hours

---

## 📋 User Story

**As a** システム管理者（Demo環境担当者）
**I want** 10台車両（2t車×5台、4t車×5台）を4拠点に適切に配分する機能
**So that** 大規模実証環境で複数拠点からの配送最適化をデモンストレーションできる

---

## 🎯 Story Context

### Existing System Integration

**Integrates with:**
- `/api/v1/seed/demo-data` エンドポイント（既存）
- `backend/app/api/v1/seed.py` のデータ生成ロジック
- `backend/app/repositories/vehicle_repository.py`
- `backend/app/services/vrp_service.py`（VRP最適化エンジン）

**Technology:**
- FastAPI + SQLAlchemy
- Python 3.12+
- OR-Tools CVRPTW（容量制約付き時間窓VRP）

**Follows pattern:**
- 既存の `Vehicle` モデルパターンを踏襲
- Repository パターンで DB アクセス
- 車両容量・コスト設定は既存の仕様を維持

**Touch points:**
- `VehicleRepository.create()` - 車両生成
- `VRPService.optimize()` - VRP最適化エンジン
- Database model: `Vehicle`
- 各拠点に紐付く車両の管理

---

## ✅ Acceptance Criteria

### Functional Requirements

1. **10台車両の正確な生成**
   - 2t車: **5台**（`vehicle-101` ～ `vehicle-105`）
   - 4t車: **5台**（`vehicle-201` ～ `vehicle-205`）
   - 各車両に固有の `vehicle_id` を付与
   - 車両タイプ別の容量・コスト設定を維持

2. **車両の拠点配分ロジック**
   - **拠点1（東京デポ）:** 2t車×2台 + 4t車×2台 = **4台**
   - **拠点2（横浜デポ）:** 2t車×1台 + 4t車×1台 = **2台**
   - **拠点3（川口デポ）:** 2t車×1台 + 4t車×1台 = **2台**
   - **拠点4（市川デポ）:** 2t車×1台 + 4t車×1台 = **2台**
   - 各車両に `depot_id` を設定（拠点との関連付け）

3. **車両タイプ別の仕様設定**

   **2t車の仕様:**
   - 容量（重量）: 2000 kg
   - 容量（容積）: 10.0 m³
   - コスト（距離）: 50 円/km
   - コスト（時間）: 2000 円/時間

   **4t車の仕様:**
   - 容量（重量）: 4000 kg
   - 容量（容積）: 20.0 m³
   - コスト（距離）: 80 円/km
   - コスト（時間）: 3000 円/時間

### Integration Requirements

4. **既存の `Vehicle` モデルパターン踏襲**
   - スキーマ変更なし
   - 既存のバリデーションルールを尊重
   - `depot_id` 外部キー制約を維持

5. **VRP最適化エンジンとの統合**
   - OR-Tools が10台車両を正しく認識すること
   - 各車両が適切な拠点から出発・帰還すること
   - 容量制約が正しく適用されること

6. **既存の車両管理機能との互換性**
   - `GET /api/v1/vehicles` エンドポイントが正常動作
   - Frontend の車両表示が正常動作
   - 車両フィルタリング機能が正常動作

### Quality Requirements

7. **データバリデーション**
   - 全車両が正しい拠点に配分されることを検証
   - 車両容量が仕様通りに設定されることを検証
   - 車両コストが仕様通りに設定されることを検証

8. **既存機能の回帰テスト**
   - Story 001-004 の機能が正常動作することを確認
   - 3台車両での最適化も引き続き動作することを確認

9. **ドキュメント更新**
   - `README.md` の「車両仕様」セクションを更新
   - 車両配分ロジックの実装ノートを作成

---

## 🛠️ Technical Notes

### Integration Approach

1. **車両生成ロジックの拡張**

   ```python
   # 車両配分仕様（拠点ごと）
   VEHICLE_ALLOCATION = {
       "depot-tokyo": {
           "2t": ["vehicle-101", "vehicle-102"],
           "4t": ["vehicle-201", "vehicle-202"],
       },
       "depot-yokohama": {
           "2t": ["vehicle-103"],
           "4t": ["vehicle-203"],
       },
       "depot-kawaguchi": {
           "2t": ["vehicle-104"],
           "4t": ["vehicle-204"],
       },
       "depot-ichikawa": {
           "2t": ["vehicle-105"],
           "4t": ["vehicle-205"],
       },
   }

   # 車両タイプ別仕様
   VEHICLE_SPECS = {
       "2t": {
           "capacity_weight": 2000,
           "capacity_volume": 10.0,
           "cost_per_km": 50,
           "cost_per_hour": 2000,
       },
       "4t": {
           "capacity_weight": 4000,
           "capacity_volume": 20.0,
           "cost_per_km": 80,
           "cost_per_hour": 3000,
       },
   }

   def create_vehicles_for_depots(depots: List[Depot]) -> List[Vehicle]:
       """
       各拠点に車両を配分して生成

       Args:
           depots: 拠点リスト（4拠点）

       Returns:
           List[Vehicle]: 生成された車両リスト（10台）
       """
       vehicles = []

       for depot in depots:
           allocation = VEHICLE_ALLOCATION.get(depot.id, {})

           # 2t車を生成
           for vehicle_id in allocation.get("2t", []):
               vehicles.append(Vehicle(
                   id=vehicle_id,
                   depot_id=depot.id,
                   vehicle_type="2t",
                   capacity_weight=VEHICLE_SPECS["2t"]["capacity_weight"],
                   capacity_volume=VEHICLE_SPECS["2t"]["capacity_volume"],
                   cost_per_km=VEHICLE_SPECS["2t"]["cost_per_km"],
                   cost_per_hour=VEHICLE_SPECS["2t"]["cost_per_hour"],
               ))

           # 4t車を生成
           for vehicle_id in allocation.get("4t", []):
               vehicles.append(Vehicle(
                   id=vehicle_id,
                   depot_id=depot.id,
                   vehicle_type="4t",
                   capacity_weight=VEHICLE_SPECS["4t"]["capacity_weight"],
                   capacity_volume=VEHICLE_SPECS["4t"]["capacity_volume"],
                   cost_per_km=VEHICLE_SPECS["4t"]["cost_per_km"],
                   cost_per_hour=VEHICLE_SPECS["4t"]["cost_per_hour"],
               ))

       return vehicles
   ```

2. **VRP最適化エンジンへの対応**

   **現在の制約:**
   - OR-Tools の `RoutingModel` は単一拠点（Single Depot）を前提としている
   - 各車両が異なる拠点から出発する場合、`starts` と `ends` パラメータで制御が必要

   **対応方針:**
   - **Phase 1（Story 5.2）:** 全車両を **拠点1（東京デポ）から出発** として扱う
     - 理由: OR-Tools の Multi-Depot 対応は複雑で、Epic 005 のスコープ外
     - 10台車両でのVRP最適化動作を優先
     - 将来的な Multi-Depot 対応は別Epicで検討

   - **Phase 2（将来検討）:** Multi-Depot VRP 対応
     - 各車両が所属拠点から出発・帰還
     - OR-Tools の `starts` / `ends` パラメータをカスタマイズ

   **実装上の注意:**
   ```python
   # VRPService.optimize() の修正（必要に応じて）
   def _create_data_model(
       self, depots: List[Depot], vehicles: List[Vehicle], deliveries: List[Delivery]
   ) -> Dict[str, Any]:
       # Phase 1: 全車両が拠点1（東京デポ）から出発
       depot_index = 0  # 拠点1のインデックス
       starts = [depot_index] * len(vehicles)
       ends = [depot_index] * len(vehicles)

       # Phase 2（将来）: 各車両が所属拠点から出発
       # starts = [depot_to_index[v.depot_id] for v in vehicles]
       # ends = [depot_to_index[v.depot_id] for v in vehicles]

       return {
           "starts": starts,
           "ends": ends,
           # ... 他のデータモデル
       }
   ```

### Existing Pattern Reference

参考実装: `backend/app/api/v1/seed.py:180-232`

既存の車両生成ロジック:
```python
# 既存: 3台車両の生成
vehicles_data = [
    Vehicle(
        id="vehicle-001",
        depot_id="depot-tokyo",
        vehicle_type="2t",
        capacity_weight=2000,
        capacity_volume=10.0,
        cost_per_km=50,
        cost_per_hour=2000,
    ),
    # ... 他の車両
]
```

**拡張方針:**
- 既存の車両生成パターンを維持
- ループで10台生成するロジックに変更
- 拠点配分ロジックを追加

### Key Constraints

- **VRP最適化の前提条件:** Phase 1 では全車両が拠点1から出発
- **パフォーマンス:** 10台車両でのVRP最適化は **10分以内** に完了すること
- **互換性:** 既存の3台車両での動作も引き続きサポート
- **スケーラビリティ:** 将来的に Multi-Depot 対応への拡張を考慮

---

## 🎯 Definition of Done

- [x] 10台車両が仕様通りに生成される（2t車×5台、4t車×5台）
- [x] 各車両が正しい拠点に配分される
- [x] 車両タイプ別の容量・コスト設定が正しい
- [x] VRP最適化が10台車両に対して動作する（拠点1から全車両出発）
- [x] 既存の3台車両での最適化も引き続き動作する
- [x] 既存の `/api/v1/vehicles` エンドポイントが正常動作する
- [x] Frontend の車両表示が正常動作する
- [x] 既存機能（Story 001-004）の回帰テストが成功する
- [x] `README.md` の車両仕様セクションが更新される
- [x] 実装ノートが作成される（Multi-Depot 対応の将来計画含む）

---

## ⚠️ Risk and Compatibility Check

### Primary Risk

**Risk:** 10台車両でのVRP最適化が計算時間超過する可能性

**Mitigation:**
- OR-Tools のタイムアウト設定を **600秒（10分）** に設定済み（Epic 005）
- メタヒューリスティクスのパラメータ調整を検討
- 必要に応じて「準最適解」でも受け入れる方針
- 計算時間のプログレス表示を実装（Story 5.3で対応）

**Rollback:**
- データ生成は既存の `DELETE FROM` クエリで全削除可能
- 既存の3台車両生成ロジックはコメント保存
- 切り戻しは `/api/v1/seed/demo-data` の再実行で対応

### Secondary Risk

**Risk:** Multi-Depot 対応の欠如（各車両が所属拠点から出発しない）

**Mitigation:**
- Phase 1 では「全車両が拠点1から出発」として実装
- ドキュメントに制約事項を明記
- 将来の Multi-Depot 対応を別Epicとして計画
- デモンストレーションには影響なし（最適化効果は十分示せる）

**Future Work:**
- Epic 006（仮）: Multi-Depot VRP 対応
- OR-Tools の `starts` / `ends` パラメータのカスタマイズ
- 距離マトリクスの拡張（複数拠点対応）

### Compatibility Verification

- [x] **No breaking changes to existing APIs**
  → `/api/v1/vehicles` のインターフェースは不変

- [x] **Database changes are additive only**
  → スキーマ変更なし（既存の `Vehicle` テーブルを使用）

- [x] **UI changes follow existing design patterns**
  → Backend のみの変更、Frontend への影響なし（Story 5.3で対応）

- [x] **Performance impact is acceptable**
  → VRP計算時間は10分以内を目標

---

## 📚 Related Documents

- [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
- [Story 5.1: 多拠点・大規模配送先データ生成機能の実装](story-5.1-multi-depot-large-scale-data-generation.md)
- [Story 5.3: UI/UX調整とパフォーマンス検証](story-5.3-ui-ux-performance-optimization.md)

---

## 📝 Implementation Checklist

### Phase 1: 車両生成ロジック拡張
- [ ] `VEHICLE_ALLOCATION` 定数定義
- [ ] `VEHICLE_SPECS` 定数定義
- [ ] `create_vehicles_for_depots()` 関数実装
- [ ] 車両生成ループの実装

### Phase 2: 拠点配分ロジック
- [ ] 各拠点に車両を紐付けるロジック実装
- [ ] `depot_id` 外部キー制約の検証
- [ ] データバリデーション関数実装

### Phase 3: VRP最適化エンジン統合
- [ ] `VRPService._create_data_model()` の調整確認
- [ ] 10台車両での最適化テスト実行
- [ ] 計算時間のモニタリング

### Phase 4: テストとバリデーション
- [ ] 単体テスト作成（`test_vehicle_allocation.py`）
- [ ] 統合テスト実行（10台車両 + 100件配送先）
- [ ] 既存機能の回帰テスト実行

### Phase 5: ドキュメント更新
- [ ] `README.md` の車両仕様セクション更新
- [ ] 実装ノート作成（Multi-Depot 対応の将来計画含む）
- [ ] API仕様書更新（必要に応じて）

---

## 🎬 Next Steps After Completion

1. **Story 5.3 開始** - UI/UX調整とパフォーマンス検証
2. **Epic 005 統合テスト** - 4拠点 + 100件 + 10台での完全動作確認
3. **Epic 006 検討** - Multi-Depot VRP 対応の計画

---

**🤖 Generated by PM Agent (John)**
**📅 Last Updated:** 2025-11-03
