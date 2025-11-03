# Story 4.1: 選択状態詳細情報表示 - Brownfield Addition

**Parent Epic:** Story 004 - Demo展示増強
**作成日:** 2025-11-03
**優先度:** High (P0)
**予定工数:** 1-2 時間
**状態:** Ready for Development

---

## User Story

**As a** Demo プレゼンター（営業・PM）,
**I want** 選択した拠点・車両・配送先の詳細データを確認できる機能,
**So that** クライアントに対してデータの正確性と専門性を示すことができる。

---

## Story Context

### Existing System Integration

**統合先コンポーネント:**
- `frontend/src/components/Control/ControlPanel.tsx` - 操作パネル

**技術スタック:**
- React 18 + TypeScript 5
- Ant Design 5 (Drawer, Descriptions, Table コンポーネント)
- Zustand (状態管理)

**既存パターン:**
- Ant Design `<Drawer>` コンポーネントの使用
- Zustand `useVRPStore` からのデータ取得
- TypeScript strict mode

**Touch Points:**
- `useVRPStore.ts`: `depots`, `vehicles`, `deliveries`, `selectedXxxIds` の取得
- `ControlPanel.tsx`: 新ボタンと Drawer の追加

---

## Acceptance Criteria

### Functional Requirements

**1. 選択状態詳細ボタンの追加**
- ControlPanel の「選択状態」表示の横に「詳細を表示」ボタンを配置
- ボタンクリックで Drawer が右側からスライドイン表示
- ボタンは選択データがある場合のみ有効化

**2. Drawer 内の詳細情報表示**

Drawer は以下の 3 セクションで構成：

**セクション 1: 拠点詳細**
```
拠点情報（1件選択中）
─────────────────
ID: depot-tokyo
名称: 東京デポ
住所: 東京都千代田区丸の内1-1-1
座標: (35.6812, 139.7671)
営業時間: 08:00 - 18:00
```

**セクション 2: 車両詳細（テーブル形式）**
```
車両一覧（3台選択中）
─────────────────────────────────────────
| 車両ID      | タイプ | 容量(重量) | 容量(体積) | コスト(km) | コスト(時) |
|------------|--------|-----------|-----------|-----------|-----------|
| vehicle-001| 2t     | 2000 kg   | 8.0 m³    | ¥50/km    | ¥2000/h   |
| vehicle-002| 2t     | 2000 kg   | 8.0 m³    | ¥50/km    | ¥2000/h   |
| vehicle-003| 4t     | 4000 kg   | 15.0 m³   | ¥80/km    | ¥3000/h   |
─────────────────────────────────────────
総容量: 8000 kg, 31.0 m³
```

**セクション 3: 配送先詳細（テーブル形式、ページネーション）**
```
配送先一覧（20件選択中）
────────────────────────────────────────────────────────────
| 配送先ID     | 顧客名      | 時間窓    | 重量   | 体積   | サービス時間 |
|-------------|-----------|----------|--------|--------|------------|
| delivery-001| 新宿商店A  | 午前指定  | 280 kg | 0.9 m³ | 15分       |
| delivery-002| 新宿商店B  | 午前指定  | 220 kg | 0.7 m³ | 10分       |
| ...         | ...       | ...      | ...    | ...    | ...        |
────────────────────────────────────────────────────────────
総重量: 5315 kg, 総体積: 16.6 m³
（ページネーション: 10件/ページ）

✅ 決定事項: 配送先は時間窓でソート（morning → afternoon → anytime）
```

**3. UI/UX 要件**
- Drawer 幅: 720px
- Drawer 位置: 右側
- 閉じるボタン: ヘッダー右上の X アイコン + 背景クリック
- スクロール: 内容が長い場合は Drawer 内でスクロール可能
- レスポンシブ: 不要（デスクトップ専用）

### Integration Requirements

**4. 既存機能の保持**
- ControlPanel の既存機能（デモデータ作成、VRP実行ボタン）が正常動作
- 選択状態サマリー表示（「選択状態: 拠点 X件...」）が引き続き表示
- Zustand store の状態変更なし（読み取りのみ）

**5. 既存パターンの踏襲**
- Ant Design `<Drawer>` コンポーネントを使用
- TypeScript strict mode 準拠
- 既存の色・フォント・スタイルを統一

**6. 統合動作**
- Drawer 表示中も地図操作可能
- Drawer 表示中も VRP 実行可能（実行時は Drawer 自動クローズ）

### Quality Requirements

**7. コード品質**
- TypeScript エラー: 0件
- ESLint 警告: 0件
- 新規コンポーネント `SelectionDetailDrawer.tsx` 作成（既存ファイル修正最小化）

**8. テスト**
- 手動テスト: 3 セクション全てのデータが正確に表示されることを確認
- リグレッションテスト: ControlPanel の既存機能が正常動作

**9. ドキュメント**
- コンポーネント内に JSDoc コメント追加
- Story 完了後、`story-004-1-completion-report.md` 作成

---

## Technical Notes

### Implementation Approach

**新規ファイル:**
```
frontend/src/components/Control/SelectionDetailDrawer.tsx
```

**修正ファイル:**
```
frontend/src/components/Control/ControlPanel.tsx
```

**実装ステップ:**

1. `SelectionDetailDrawer.tsx` 作成
   ```tsx
   interface SelectionDetailDrawerProps {
     visible: boolean;
     onClose: () => void;
   }

   export const SelectionDetailDrawer: React.FC<...> = ({ visible, onClose }) => {
     const { depots, vehicles, deliveries, selectedDepotIds, ... } = useVRPStore();

     // 選択されたデータをフィルタ
     const selectedDepots = depots.filter(d => selectedDepotIds.includes(d.id));
     const selectedVehicles = vehicles.filter(v => selectedVehicleIds.includes(v.id));
     const selectedDeliveries = deliveries.filter(d => selectedDeliveryIds.includes(d.id));

     // ✅ 決定事項: 配送先を時間窓でソート
     const sortedDeliveries = selectedDeliveries.sort((a, b) => {
       const timeWindowOrder = { morning: 1, afternoon: 2, anytime: 3 };
       return timeWindowOrder[a.time_window] - timeWindowOrder[b.time_window];
     });

     return (
       <Drawer title="選択状態詳細" placement="right" width={720} visible={visible} onClose={onClose}>
         {/* セクション 1: 拠点詳細 */}
         <Descriptions title={`拠点情報（${selectedDepots.length}件選択中）`} bordered>
           {/* ... */}
         </Descriptions>

         {/* セクション 2: 車両詳細 */}
         <Table
           title={() => `車両一覧（${selectedVehicles.length}台選択中）`}
           dataSource={selectedVehicles}
           columns={vehicleColumns}
           pagination={false}
         />

         {/* セクション 3: 配送先詳細 */}
         <Table
           title={() => `配送先一覧（${selectedDeliveries.length}件選択中）`}
           dataSource={sortedDeliveries}  {/* ✅ ソート済みデータを使用 */}
           columns={deliveryColumns}
           pagination={{ pageSize: 10 }}
         />
       </Drawer>
     );
   };
   ```

2. `ControlPanel.tsx` 修正
   ```tsx
   const [detailsVisible, setDetailsVisible] = useState(false);

   // 既存の「選択状態」表示の横に追加
   <Space>
     <Text>選択状態: 拠点 {selectedDepotIds.length}件...</Text>
     <Button
       size="small"
       onClick={() => setDetailsVisible(true)}
       disabled={selectedDepotIds.length === 0}
     >
       詳細を表示
     </Button>
   </Space>

   <SelectionDetailDrawer
     visible={detailsVisible}
     onClose={() => setDetailsVisible(false)}
   />
   ```

### Existing Pattern Reference

**Ant Design Drawer 使用例:**
- 公式ドキュメント: https://ant.design/components/drawer/
- Placement: "right"
- Width: 720 (推奨)
- closable: true (デフォルト)

**Table Columns 定義パターン:**
```tsx
const deliveryColumns = [
  { title: '配送先ID', dataIndex: 'id', key: 'id', width: 120 },
  { title: '顧客名', dataIndex: 'customer_name', key: 'name', width: 120 },
  { title: '時間窓', dataIndex: 'time_window', key: 'time', width: 100,
    render: (tw) => tw === 'morning' ? '午前指定' : tw === 'afternoon' ? '午後指定' : '指定なし'
  },
  { title: '重量', dataIndex: 'weight', key: 'weight', width: 80,
    render: (w) => `${w} kg`
  },
  // ...
];
```

### Key Constraints

- **Zero Backend Changes:** Frontend のみの実装
- **Zero New Dependencies:** 既存ライブラリのみ使用
- **Minimal Code Impact:** 新規コンポーネント追加、既存コード修正最小
- **Desktop Only:** レスポンシブ対応不要（1920×1080 想定）

---

## Definition of Done

### 完了チェックリスト

- [ ] **機能実装完了**
  - [ ] SelectionDetailDrawer.tsx 作成完了
  - [ ] ControlPanel.tsx に「詳細を表示」ボタン追加
  - [ ] Drawer 内に 3 セクション実装（拠点・車両・配送先）

- [ ] **データ表示正確性**
  - [ ] 拠点詳細: ID, 名称, 住所, 座標, 営業時間 表示
  - [ ] 車両詳細: 全選択車両のスペック、総容量 表示
  - [ ] 配送先詳細: 全選択配送先のデータ、ページネーション動作

- [ ] **統合要件**
  - [ ] 既存の ControlPanel 機能が正常動作（リグレッションなし）
  - [ ] Drawer 表示中も地図操作可能
  - [ ] Drawer 表示中も VRP 実行可能

- [ ] **コード品質**
  - [ ] TypeScript エラー: 0件
  - [ ] ESLint 警告: 0件
  - [ ] JSDoc コメント追加

- [ ] **テスト**
  - [ ] 手動テスト: 3 セクション全てのデータ正確性確認
  - [ ] リグレッションテスト: Story 003 全機能正常動作

- [ ] **ドキュメント**
  - [ ] `story-004-1-completion-report.md` 作成
  - [ ] コード内コメント完備

---

## Risk and Compatibility Check

### Minimal Risk Assessment

**Primary Risk:**
ControlPanel.tsx 修正による既存機能への影響

**Mitigation:**
- 新機能は独立コンポーネント（SelectionDetailDrawer）として実装
- ControlPanel.tsx の修正は最小限（ボタン追加のみ）
- useState による状態管理、Zustand store は読み取りのみ

**Rollback:**
- SelectionDetailDrawer.tsx を削除
- ControlPanel.tsx の追加コード（ボタン + Drawer コンポーネント）を削除
- 10分以内でロールバック可能

### Compatibility Verification

- [x] **No Breaking Changes:** 既存 API 不変
- [x] **Database:** 変更なし
- [x] **UI Patterns:** Ant Design パターン踏襲
- [x] **Performance:** 影響なし（新規 API コールなし、レンダリングコスト低）

---

## Validation Checklist

### Scope Validation

- [x] **Single Session:** 1-2 時間で完了可能
- [x] **Straightforward Integration:** Zustand store からデータ取得のみ
- [x] **Existing Patterns:** Ant Design Drawer/Table パターン使用
- [x] **No Design Work:** UI デザイン確定済み

### Clarity Check

- [x] **Unambiguous Requirements:** AC に具体的なデータ項目明記
- [x] **Clear Integration Points:** ControlPanel.tsx, useVRPStore.ts 明確
- [x] **Testable Criteria:** 手動テストで全データ確認可能
- [x] **Simple Rollback:** ファイル削除 + コード削除のみ

---

## Success Criteria

Story 4.1 の成功基準:

1. ✅ 「詳細を表示」ボタンクリックで Drawer が表示される
2. ✅ 拠点・車両・配送先の詳細データが正確に表示される
3. ✅ 配送先テーブルのページネーションが正常動作する
4. ✅ 既存の ControlPanel 機能（デモデータ作成、VRP実行）が正常動作する
5. ✅ TypeScript/ESLint エラーなし
6. ✅ クライアントに見せてデータの専門性が伝わる

---

**Created by:** Product Manager (John)
**Reviewed by:** Pending
**Status:** Ready for Development
**Next:** Story 4.2 - 最適化前後方案対比
