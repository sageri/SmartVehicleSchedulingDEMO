# Story 004: Demo展示增強 - Brownfield Enhancement

**作成日:** 2025-11-03
**優先度:** High
**予定工数:** 5-7 時間（Backend 変更含む）
**状態:** ✅ 完了（2025-11-03）

---

## Epic Goal

Demo展示の専門性と説得力を向上させるため、詳細なデータ表示と視覚的な改善を追加し、クライアントがVRP最適化の価値を直感的に理解できるようにする。

---

## Epic Description

### Existing System Context

**現在の関連機能:**
- Story 003完了：React Frontend + Backend API 完全統合
- OpenStreetMap地図表示（拠点・配送先マーカー、ルートPolyline）
- 結果パネル（概要、ルート一覧、コスト比較）
- 操作パネル（デモデータ作成、VRP実行）

**技術スタック:**
- **Frontend:** React 18 + TypeScript 5 + Ant Design 5 + Leaflet
- **Backend:** FastAPI + Python 3.11 + OR-Tools
- **状態管理:** Zustand

**統合ポイント:**
- `frontend/src/components/Control/ControlPanel.tsx` - 操作パネル
- `frontend/src/components/Result/ResultPanel.tsx` - 結果表示
- `frontend/src/components/Map/RoutePolyline.tsx` - ルート描画
- `frontend/src/stores/useVRPStore.ts` - グローバル状態

### Enhancement Details

**追加・変更内容:**

1. **選択状態詳細情報表示**
   - 現状：「選択状態: 拠点 1件, 車両 3台, 配送先 20件」（数量のみ）
   - 改善：Drawer/Modal で詳細データ表示（拠点名、車両スペック、配送先一覧）

2. **最適化前後方案対比**
   - 現状：改善指標のみ表示（距離削減率、コスト削減率）
   - 改善：基線方案と最適化後方案の完全なデータを並列表示

3. **ルート方向矢印**
   - 現状：Polyline のみ、方向不明
   - 改善：ルート上に方向矢印を追加

**統合アプローチ:**
- 既存の Ant Design コンポーネントパターンを踏襲
- Zustand store から既存データを活用、新規 API 不要
- 既存レイアウトを維持、新機能は独立コンポーネントとして追加

**成功基準:**
- クライアントが詳細データを容易に確認できる
- 最適化の価値（Before/After）が視覚的に明確
- Demo の専門性と説得力が向上
- 既存機能に影響なし（リグレッションなし）

---

## Stories

### Story 4.1: 選択状態詳細情報表示（Drawer実装）

**概要:**
ControlPanel に「選択状態詳細を表示」ボタンを追加し、Ant Design Drawer で拠点・車両・配送先の詳細データを表形式で表示する。

**開発時間:** 1-2 時間

**主要タスク:**
1. `SelectionDetailDrawer.tsx` 新規コンポーネント作成
2. Zustand store から選択データ取得
3. 3つのセクション実装（拠点詳細、車両詳細、配送先詳細）
4. Drawer 開閉状態管理

**技術詳細:**
- Ant Design `<Drawer>` + `<Descriptions>` / `<Table>` コンポーネント使用
- `useVRPStore` から `depots`, `vehicles`, `deliveries`, `selectedXxxIds` 取得
- 既存 `ControlPanel.tsx` に統合

---

### Story 4.2: 最適化前後方案対比表示（新規Tab）

**概要:**
ResultPanel に新しい Tab「方案対比」を追加し、基線方案（simple_assignment）と最適化後方案（OR-Tools）の詳細データを並列表示する。

**開発時間:** 2-3 小時

**主要タスク:**
1. `ComparisonTab.tsx` 新規コンポーネント作成
2. 基線 vs 最適化の比較テーブル実装（ルート数、総距離、総コスト、平均積載率）
3. ルート別詳細比較（各ルートの距離・コスト・停車数）
4. ResultPanel の tabItems に追加
5. **Backend API 修正:** `baseline_metrics.vehicle_count` フィールド追加（30-60分）

**技術詳細:**
- `optimizationResult.baseline_metrics` と最適化結果を比較
- ✅ **決定事項:** Backend から `vehicle_count` を取得（推定値ではなく正確な値）
- ✅ **決定事項:** 改善率表示は「絶対値 + 百分比」形式（例: `+19.5 pt (+100%)`）
- Ant Design `<Table>` で並列表示、差分をハイライト
- 改善率を視覚化（緑=改善、赤=悪化）

---

### Story 4.3: ルート方向矢印可視化

**概要:**
地図上のルート Polyline に方向矢印を追加し、車両の移動方向を視覚的に表示する。

**開発時間:** 1 時間

**主要タスク:**
1. `RoutePolyline.tsx` 修正
2. ルート中点位置計算
3. 方向角度計算（始点→終点）
4. Leaflet Marker + DivIcon で矢印表示

**技術詳細:**
- ルート座標配列の中点を取得
- `Math.atan2()` で角度計算
- CSS `transform: rotate()` で矢印回転
- 各ルートの色に合わせた矢印色

---

## Compatibility Requirements

- [x] データベーススキーマ変更なし
- [x] UI は既存 Ant Design パターンに準拠
- [x] パフォーマンス影響は無視できるレベル（新規 API コールなし）
- ⚠️ **Backend API 変更:** `baseline_metrics.vehicle_count` フィールド追加（最小限の変更）

---

## Risk Mitigation

**主要リスク:**
既存の ControlPanel / ResultPanel / RoutePolyline コンポーネント修正によるリグレッション

**軽減策:**
- 新機能は独立コンポーネントとして実装（既存コードへの影響最小化）
- Drawer / Tab は既存レイアウトに追加、既存機能を置換しない
- 矢印は Polyline とは別 Layer に配置、既存ルート描画ロジック不変

**ロールバック計画:**
- Story 単位で Git コミット分離
- 問題発生時は該当 Story のコミットを revert
- フィーチャーフラグ不要（UI 追加のみ、破壊的変更なし）

---

## Definition of Done

- [x] **Story 4.1 完了:** 選択状態詳細 Drawer が正常動作、全データ正確表示
- [x] **Story 4.2 完了:** 方案対比 Tab が正常動作、基線 vs 最適化の差分明確
- [x] **Story 4.3 完了:** ルート矢印が全ルートに表示、方向正確
- [x] **統合テスト:** 3 機能が同時動作、相互干渉なし
- [x] **既存機能検証:** Story 003 の全機能が正常動作（リグレッションなし）
- [x] **ドキュメント更新:** README.md 更新完了
- [x] **コードレビュー:** TypeScript エラーなし、Lint 警告なし
- [x] **Git提交:** 6次原子提交完成（規画 + Backend + 3 Stories + 優化）

---

## Technical Notes

### 既存パターン参照

**Drawer パターン:**
- 参考: Ant Design `<Drawer>` 公式ドキュメント
- 幅: 720px（デフォルト）
- Placement: "right"

**Tab 追加パターン:**
- 参考: `ResultPanel.tsx` 既存の `tabItems` 配列
- 新 Tab を配列に追加するだけ、既存コード変更最小

**Leaflet Marker パターン:**
- 参考: `DepotMarker.tsx`, `DeliveryMarker.tsx`
- DivIcon を使用した HTML ベースアイコン

### Key Constraints

- **Zero 新規依赴:** 既存ライブラリのみ使用（追加インストール不要）
- **Zero API 変更:** Backend 修正不要、Frontend のみ
- **既存デザイン準拠:** Ant Design テーマ、色使い、フォント統一
- **レスポンシブ不要:** デスクトップ Demo 専用（1920×1080 想定）

---

## Story Manager Handoff

"Please develop detailed user stories for this brownfield epic. Key considerations:

- This is an enhancement to an existing React + TypeScript frontend running Ant Design 5 + Leaflet
- Integration points: ControlPanel.tsx, ResultPanel.tsx, RoutePolyline.tsx, useVRPStore.ts
- Existing patterns to follow: Ant Design component usage, Zustand state management, TypeScript strict mode
- Critical compatibility requirements: No backend changes, no breaking changes to existing components, maintain current UI layout
- Each story must include verification that existing Story 003 functionality remains intact

The epic should maintain system integrity while delivering enhanced demo presentation capabilities for client meetings."

---

## 参考資料

- **既存実装:** `docs/story-003-completion-report.md`
- **技術スタック:** `README.md`
- **コンポーネント構造:** `frontend/src/components/`
- **API 仕様:** `backend/docs/API_GUIDE.md`（参照のみ、変更なし）

---

**Created by:** Product Manager (John)
**Approved by:** Pending
**Next Milestone:** Story 005 または Demo 本番準備
