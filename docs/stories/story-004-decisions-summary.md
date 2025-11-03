# Story 004 - 決定事項総括

**作成日:** 2025-11-03
**決定者:** ユーザー（Product Owner）
**文書状態:** 最終確定

---

## 📋 背景

Story 004（Demo展示増強）の実装に際し、3つの設計上の決定事項を確認しました。

---

## ✅ 決定事項一覧

### 決定事項 1: 基線車両数データ来源

**問題:**
- Backend API の `baseline_metrics` に `vehicle_count` フィールドが存在しない
- 前端で推定するか、後端で追加するか、または表示しないか

**選択肢:**
- A. 後端で `vehicle_count` フィールドを追加（最も正確）
- B. 車両数対比を表示しない（最も保守的）
- C. 前端で推定値を使用 + "推定値"と明記（折衷案）

**最終決定:** ✅ **選択肢 A - 後端でフィールドを追加**

**理由:**
- Demo の価値提案に「車両削減」は重要な指標
- 推定値ではクライアントの信頼を損なう可能性
- 後端変更は最小限（1行追加、30-60分）

**影響範囲:**
- 修正ファイル: `backend/app/services/vrp_solver.py`
- 追加フィールド: `baseline_metrics.vehicle_count: int`
- 追加工数: 30-60分
- Story 予定工数: 4-6時間 → 5-7時間

---

### 決定事項 2: 改善率表示方式

**問題:**
- 積載率改善を `+100%` と表示すると「積載率が100%になった」と誤解される可能性
- 絶対値（+19.5 pt）のみでは改善幅が分かりにくい

**選択肢:**
- A. 絶対値 + 百分比（`+19.5 pt (+100%)`）
- B. 絶対値のみ（`+19.5 pt`）
- C. 百分比のみ（`+100%`）

**最終決定:** ✅ **選択肢 A - 絶対値 + 百分比**

**理由:**
- 絶対値で実際の変化が明確（19.5% → 39.0%）
- 百分比で改善率の大きさが分かる（100%改善は2倍）
- 両方表示することで誤解を防ぐ

**実装例:**
```typescript
// 積載率改善の表示
const improvement = result.average_utilization_weight - baseline_metrics.average_utilization_weight;
const improvementPercent = (improvement / baseline_metrics.average_utilization_weight) * 100;

display: `+${improvement.toFixed(1)} pt (+${improvementPercent.toFixed(1)}%)`
// 出力: "+19.5 pt (+100%)"
```

**影響範囲:**
- 修正コンポーネント: `ComparisonTab.tsx`
- 追加工数: 0分（既定の実装内）

---

### 決定事項 3: 配送先テーブルの並び順

**問題:**
- Story 4.1 の Drawer 内の配送先一覧テーブルの並び順が未定義
- ID順、選択順、時間窓順、距離順などの選択肢

**選択肢:**
- A. 簡単な時間窓ソート（morning → afternoon → anytime）
- B. 時間窓 + 距離ソート（各時間窓内で距離順）
- C. ユーザーがクリックして並び替え可能（Ant Design の sorter 機能）

**最終決定:** ✅ **選択肢 A - 簡単な時間窓ソート**

**理由:**
- Demo 展示の目的は「時間制約の可視化」
- 時間窓でグループ化することでクライアントが理解しやすい
- 実装が最もシンプル（5分）

**実装例:**
```typescript
const sortedDeliveries = selectedDeliveries.sort((a, b) => {
  const timeWindowOrder = { morning: 1, afternoon: 2, anytime: 3 };
  return timeWindowOrder[a.time_window] - timeWindowOrder[b.time_window];
});
```

**影響範囲:**
- 修正コンポーネント: `SelectionDetailDrawer.tsx`
- 追加工数: 5分

---

## 📊 決定事項の影響総括

| 項目 | 変更前 | 変更後 |
|-----|--------|--------|
| **Backend 変更** | なし | `vrp_solver.py` に 1 フィールド追加 |
| **予定工数** | 4-6時間 | 5-7時間 |
| **実装範囲** | Frontend のみ | Frontend + Backend（最小限） |
| **データ精度** | 一部推定値 | 全て実測値 |
| **クライアント価値** | 中 | 高（車両削減を明確に証明） |

---

## 🎯 更新された実装計画

### 実装順序

1. **Backend 変更** (30-60分)
   - `vrp_solver.py` の baseline 計算ロジックに `vehicle_count` 追加
   - API レスポンスの確認

2. **Story 4.1** (1-2時間)
   - `SelectionDetailDrawer.tsx` 作成
   - 配送先を時間窓でソート

3. **Story 4.2** (2-3時間)
   - `ComparisonTab.tsx` 作成
   - Backend の `vehicle_count` を使用
   - 改善率を「絶対値 + 百分比」で表示

4. **Story 4.3** (1時間)
   - `RoutePolyline.tsx` に方向矢印追加

5. **テスト & 文書** (30分)
   - 手動テスト
   - 完了報告書作成

**合計予定時間:** 5-7時間

---

## 📝 リスクと緩和策

### リスク 1: Backend 変更によるリグレッション

**緩和策:**
- 変更は baseline 計算ロジックのみ（既存の最適化ロジックに影響なし）
- API レスポンススキーマは後方互換（フィールド追加のみ）
- Frontend は新フィールド不在時の fallback 実装（古い API でも動作）

### リスク 2: 時間超過

**緩和策:**
- Backend 変更を最初に実施（ブロッカーを早期解決）
- Story 4.1-4.3 は独立（並行開発可能）
- 各 Story 完了後に Git コミット（ロールバック可能）

---

## ✅ 承認

- **決定者:** ユーザー（Product Owner）
- **承認日:** 2025-11-03
- **次のステップ:** 実装開始

---

**署名:**
決定事項は全て確認され、実装可能と判断されました。

---

**参照文書:**
- `docs/stories/story-004-demo-enhancement.md` - Epic 文書
- `docs/stories/story-004-1-selection-detail-drawer.md` - Story 4.1
- `docs/stories/story-004-2-comparison-tab.md` - Story 4.2（決定事項反映済み）
- `docs/stories/story-004-3-route-arrows.md` - Story 4.3
