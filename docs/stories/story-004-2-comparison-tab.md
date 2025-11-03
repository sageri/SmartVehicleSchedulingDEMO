# Story 4.2: 最適化前後方案対比表示 - Brownfield Addition

**Parent Epic:** Story 004 - Demo展示増強
**作成日:** 2025-11-03
**優先度:** High (P0)
**予定工数:** 2-3 時間
**状態:** Ready for Development

---

## User Story

**As a** Demo プレゼンター（営業・PM）,
**I want** 最適化前後の方案を並列表示して比較できる機能,
**So that** クライアントに対して最適化の価値（改善効果）を視覚的に証明できる。

---

## Story Context

### Existing System Integration

**統合先コンポーネント:**
- `frontend/src/components/Result/ResultPanel.tsx` - 結果パネル（既存 3 タブ）

**技術スタック:**
- React 18 + TypeScript 5
- Ant Design 5 (Tabs, Table, Statistic, Tag コンポーネント)
- Zustand (状態管理)

**既存パターン:**
- Ant Design `<Tabs>` コンポーネント（既に 3 タブ実装済み）
- `tabItems` 配列に新 Tab を追加するだけ
- Zustand `useVRPStore` から `optimizationResult` 取得

**Touch Points:**
- `useVRPStore.ts`: `optimizationResult.baseline_metrics` と最適化結果の取得
- `ResultPanel.tsx`: `tabItems` 配列に新 Tab 追加

**既存データ構造:**
```typescript
interface OptimizationResult {
  routes: Route[];                    // 最適化後のルート
  total_distance: number;
  total_cost: number;
  average_utilization_weight: number;
  baseline_metrics: {                 // 基線方案（simple_assignment）
    total_distance: number;
    total_duration: number;
    total_cost: number;
    average_utilization_weight: number;
    method: string;
  };
  improvement_metrics: {              // 改善指標
    distance_reduction_km: number;
    distance_reduction_percent: number;
    cost_reduction_amount: number;
    cost_reduction_percent: number;
    utilization_improvement_percent: number;
  };
}
```

---

## Acceptance Criteria

### Functional Requirements

**1. 新 Tab「方案対比」の追加**
- ResultPanel の既存 3 タブ（概要、ルート一覧、コスト比較）に 4 番目のタブとして追加
- タブ名: 「方案対比」
- アイコン: `<SwapOutlined />` (Ant Design Icon)
- 最適化結果が存在する場合のみ表示

**2. 総合比較セクション（上部カード）**

4 つの比較指標を横並びで表示：

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   総距離     │   総コスト    │  平均積載率   │   使用車両   │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ 基線: 43.3km │ 基線: ¥7,734 │ 基線: 19.5%  │ 基線: 4台    │
│ 最適: 48.1km │ 最適: ¥8,338 │ 最適: 39.0%  │ 最適: 1台    │
│ 差分: -4.8km │ 差分: -¥604  │ 改善: +19.5% │ 削減: 3台    │
│  (-11.0%)   │   (-7.8%)    │  (100%改善)  │  (75%削減)   │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**表示仕様:**
- Ant Design `<Statistic>` コンポーネント使用
- 差分の色分け:
  - 緑（#52c41a）: 改善（距離減少、コスト減少、積載率向上）
  - 赤（#ff4d4f）: 悪化（距離増加、コスト増加）
  - 青（#1890ff）: 中立（車両数）
- 各指標に改善率（%）を表示

**3. ルート別詳細比較テーブル（下部）**

```
ルート別比較表
─────────────────────────────────────────────────────────────
| 比較項目         | 基線方案            | 最適化方案          | 差分        |
|-----------------|--------------------|--------------------|-------------|
| 使用車両数       | 4台                | 1台                | -3台 (-75%) |
| 総停車数         | 6件                | 6件                | 0件 (0%)    |
| 総距離           | 43.34 km           | 48.09 km           | +4.75 km (+11%) |
| 総所要時間       | 2時間47分          | 2時間58分          | +11分 (+7%)  |
| 総コスト         | ¥7,734             | ¥8,338             | +¥604 (+8%) |
| 平均積載率（重量）| 19.5%              | 39.0%              | +19.5% (+100%) |
| 距離/停車数      | 7.22 km/件         | 8.02 km/件         | +0.80 km    |
| コスト/停車数    | ¥1,289/件          | ¥1,390/件          | +¥101       |
─────────────────────────────────────────────────────────────
```

**表示仕様:**
- Ant Design `<Table>` コンポーネント
- 3 列構成:「基線方案」「最適化方案」「差分」
- 差分列は改善/悪化で色分け（Tag コンポーネント使用）
- ページネーション不要（データ量少ない）

**4. 基線方案の説明セクション**

テーブル上部に Info アラート表示：

```
ℹ️ 基線方案について
基線方案は「simple_assignment」アルゴリズムで生成されています。
これは最も単純な割当方式で、最適化前の状態を示します。
OR-Tools による最適化との差分が改善効果を表します。
```

**5. データ不足時の対応**

- `baseline_metrics` が存在しない場合:
  - Empty State を表示
  - メッセージ: 「基線方案データが利用できません」

### Integration Requirements

**6. 既存機能の保持**
- ResultPanel の既存 3 タブが正常動作
- Tab 切り替えがスムーズ
- 最適化実行後に自動的に「方案対比」タブを表示（初回表示用）

**7. 既存パターンの踏襲**
- Ant Design `<Tabs>` の `tabItems` 配列パターン
- TypeScript strict mode 準拠
- 既存の色・フォント・スタイルを統一

**8. 統合動作**
- Tab 表示中も地図操作可能
- Tab 表示中も VRP 再実行可能
- 新規最適化実行時は自動的に「方案対比」タブに切り替え（UX 向上）

### Quality Requirements

**9. コード品質**
- TypeScript エラー: 0件
- ESLint 警告: 0件
- 新規コンポーネント `ComparisonTab.tsx` 作成（既存ファイル修正最小化）

**10. テスト**
- 手動テスト: 4 指標と詳細テーブルのデータ正確性確認
- エッジケーステスト: baseline_metrics 不足時の Empty State 表示確認
- リグレッションテスト: 既存 3 タブの正常動作確認

**11. ドキュメント**
- コンポーネント内に JSDoc コメント追加
- Story 完了後、`story-004-2-completion-report.md` 作成

---

## Technical Notes

### Implementation Approach

**新規ファイル:**
```
frontend/src/components/Result/ComparisonTab.tsx
```

**修正ファイル:**
```
frontend/src/components/Result/ResultPanel.tsx
```

**実装ステップ:**

**Step 1: ComparisonTab.tsx 作成**

```tsx
import { Statistic, Table, Alert, Card, Row, Col, Tag } from 'antd';
import { SwapOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { useVRPStore } from '@/stores/useVRPStore';
import type { OptimizationResult } from '@/types';

interface ComparisonTabProps {
  result: OptimizationResult;
}

/**
 * 最適化前後の方案対比表示コンポーネント
 *
 * 基線方案（simple_assignment）と最適化後方案の詳細データを並列表示し、
 * 改善効果を視覚的に示します。
 */
export const ComparisonTab: React.FC<ComparisonTabProps> = ({ result }) => {
  const { baseline_metrics, improvement_metrics } = result;

  // 基線データがない場合の Empty State
  if (!baseline_metrics) {
    return (
      <Alert
        message="基線方案データが利用できません"
        description="最適化結果に基線方案の情報が含まれていません。"
        type="warning"
        showIcon
      />
    );
  }

  // 使用車両数の計算
  const baselineVehicleCount = baseline_metrics.method === 'simple_assignment'
    ? Math.ceil(result.routes.length * 1.5) // 推定値（実際のデータに基づく）
    : result.routes.length;
  const optimizedVehicleCount = result.routes.length;

  // 総合比較データ
  const summaryStats = [
    {
      title: '総距離',
      baseline: `${baseline_metrics.total_distance.toFixed(2)} km`,
      optimized: `${result.total_distance.toFixed(2)} km`,
      diff: improvement_metrics.distance_reduction_km,
      percent: improvement_metrics.distance_reduction_percent,
    },
    {
      title: '総コスト',
      baseline: `¥${baseline_metrics.total_cost.toLocaleString()}`,
      optimized: `¥${result.total_cost.toLocaleString()}`,
      diff: improvement_metrics.cost_reduction_amount,
      percent: improvement_metrics.cost_reduction_percent,
    },
    {
      title: '平均積載率',
      baseline: `${baseline_metrics.average_utilization_weight.toFixed(1)}%`,
      optimized: `${result.average_utilization_weight.toFixed(1)}%`,
      diff: improvement_metrics.utilization_improvement_percent,
      percent: improvement_metrics.utilization_improvement_percent,
    },
    {
      title: '使用車両',
      baseline: `${baselineVehicleCount}台`,
      optimized: `${optimizedVehicleCount}台`,
      diff: optimizedVehicleCount - baselineVehicleCount,
      percent: ((optimizedVehicleCount - baselineVehicleCount) / baselineVehicleCount) * 100,
    },
  ];

  // ルート別詳細比較テーブルのデータ
  const detailTableData = [
    {
      key: 'vehicle_count',
      metric: '使用車両数',
      baseline: `${baselineVehicleCount}台`,
      optimized: `${optimizedVehicleCount}台`,
      diff: `${optimizedVehicleCount - baselineVehicleCount}台`,
      diffPercent: (((optimizedVehicleCount - baselineVehicleCount) / baselineVehicleCount) * 100).toFixed(1),
    },
    // ... 其他指标
  ];

  // Table columns 定義
  const columns = [
    {
      title: '比較項目',
      dataIndex: 'metric',
      key: 'metric',
      width: 150,
    },
    {
      title: '基線方案',
      dataIndex: 'baseline',
      key: 'baseline',
      width: 150,
    },
    {
      title: '最適化方案',
      dataIndex: 'optimized',
      key: 'optimized',
      width: 150,
    },
    {
      title: '差分',
      dataIndex: 'diff',
      key: 'diff',
      width: 150,
      render: (text: string, record: any) => {
        const isImprovement = parseFloat(record.diffPercent) < 0; // 负值是改善
        return (
          <Tag color={isImprovement ? 'success' : 'error'} icon={isImprovement ? <ArrowDownOutlined /> : <ArrowUpOutlined />}>
            {text} ({record.diffPercent}%)
          </Tag>
        );
      },
    },
  ];

  return (
    <div style={{ padding: '16px' }}>
      {/* 基线方案说明 */}
      <Alert
        message="基線方案について"
        description={`基線方案は「${baseline_metrics.method}」アルゴリズムで生成されています。これは最も単純な割当方式で、最適化前の状態を示します。OR-Tools による最適化との差分が改善効果を表します。`}
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* 总合比较卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {summaryStats.map((stat, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.diff}
                precision={2}
                valueStyle={{
                  color: stat.diff < 0 ? '#52c41a' : stat.diff > 0 ? '#ff4d4f' : '#1890ff',
                  fontSize: 24,
                }}
                prefix={stat.diff < 0 ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
                suffix={`(${stat.percent.toFixed(1)}%)`}
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
                <div>基線: {stat.baseline}</div>
                <div>最適: {stat.optimized}</div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 路线别详细比较表 */}
      <Card title="ルート別詳細比較" bordered={false}>
        <Table
          dataSource={detailTableData}
          columns={columns}
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
};
```

**Step 2: ResultPanel.tsx 修正**

```tsx
import { ComparisonTab } from './ComparisonTab';
import { SwapOutlined } from '@ant-design/icons';

// 既存の tabItems 配列に追加
const tabItems = [
  {
    key: 'summary',
    label: '概要',
    icon: <InfoCircleOutlined />,
    children: <SummaryTab result={optimizationResult} />,
  },
  {
    key: 'routes',
    label: 'ルート一覧',
    icon: <CarOutlined />,
    children: <RoutesTab result={optimizationResult} />,
  },
  {
    key: 'cost',
    label: 'コスト比較',
    icon: <BarChartOutlined />,
    children: <CostComparisonTab result={optimizationResult} />,
  },
  {
    key: 'comparison',  // 新規追加
    label: '方案対比',
    icon: <SwapOutlined />,
    children: <ComparisonTab result={optimizationResult} />,
  },
];

// 最適化実行後に「方案対比」タブに自動切替（オプション）
useEffect(() => {
  if (optimizationResult && optimizationResult.baseline_metrics) {
    setActiveTab('comparison');
  }
}, [optimizationResult]);
```

### Data Transformation

**基线方案车辆数数据来源:**

✅ **決定事項:** Backend API に `baseline_metrics.vehicle_count` フィールドを追加

```typescript
// Backend API レスポンス（更新後）
interface BaselineMetrics {
  vehicle_count: number;        // ✅ 新規追加フィールド
  total_distance: number;
  total_duration: number;
  total_cost: number;
  average_utilization_weight: number;
  method: string;
}

// Frontend 使用例
const baselineVehicleCount = baseline_metrics.vehicle_count;
const optimizedVehicleCount = result.routes.length;
```

**Backend 修正範囲:** `backend/app/services/vrp_solver.py` の `baseline_metrics` 計算ロジック

**改善率表示方式:**

✅ **決定事項:** 絶対値 + 百分比を同時表示

```typescript
// 積載率改善の表示例
const utilizationImprovement = {
  absolute: `+${improvement_metrics.utilization_improvement_percent.toFixed(1)} pt`,
  relative: `(+${((improvement - baseline) / baseline * 100).toFixed(1)}%)`
};
// 表示: "+19.5 pt (+100%)"
```

### Key Constraints

- **Backend Changes Required:** `baseline_metrics.vehicle_count` フィールド追加（30-60分）
- **Zero New Dependencies:** 既存ライブラリのみ使用
- **Minimal Code Impact:**
  - Frontend: 新規コンポーネント追加、ResultPanel は Tab 追加のみ
  - Backend: `vrp_solver.py` の baseline 計算ロジックに 1 行追加
- **Desktop Only:** レスポンシブ対応不要（1920×1080 想定）

---

## Definition of Done

### 完了チェックリスト

- [ ] **機能実装完了**
  - [ ] ComparisonTab.tsx 作成完了
  - [ ] ResultPanel.tsx に「方案対比」タブ追加
  - [ ] 4 つの総合比較指標カード実装
  - [ ] ルート別詳細比較テーブル実装

- [ ] **データ表示正確性**
  - [ ] 総距離、総コスト、平均積載率、使用車両の差分が正確
  - [ ] 改善/悪化の色分けが正確（緑=改善、赤=悪化）
  - [ ] 基線方案説明アラートが表示される
  - [ ] Empty State が baseline_metrics 不足時に表示される

- [ ] **統合要件**
  - [ ] 既存 3 タブが正常動作（リグレッションなし）
  - [ ] Tab 切り替えがスムーズ
  - [ ] 最適化実行後に自動的に「方案対比」タブに切り替わる（オプション）

- [ ] **コード品質**
  - [ ] TypeScript エラー: 0件
  - [ ] ESLint 警告: 0件
  - [ ] JSDoc コメント追加

- [ ] **テスト**
  - [ ] 手動テスト: 4 指標と詳細テーブルのデータ正確性確認
  - [ ] Empty State テスト: baseline_metrics 不足時の表示確認
  - [ ] リグレッションテスト: Story 003 全機能正常動作

- [ ] **ドキュメント**
  - [ ] `story-004-2-completion-report.md` 作成
  - [ ] コード内コメント完備

---

## Risk and Compatibility Check

### Minimal Risk Assessment

**Primary Risk:**
ResultPanel.tsx 修正による既存 3 タブへの影響

**Mitigation:**
- 新機能は独立コンポーネント（ComparisonTab）として実装
- ResultPanel.tsx の修正は最小限（tabItems 配列に 1 項目追加のみ）
- 既存 Tab コンポーネントへの影響なし

**Rollback:**
- ComparisonTab.tsx を削除
- ResultPanel.tsx の `tabItems` から「方案対比」エントリを削除
- 5分以内でロールバック可能

### Compatibility Verification

- [x] **No Breaking Changes:** 既存 API 不変
- [x] **Database:** 変更なし
- [x] **UI Patterns:** Ant Design パターン踏襲
- [x] **Performance:** 影響なし（新規 API コールなし、レンダリングコスト低）

---

## Validation Checklist

### Scope Validation

- [x] **Single Session:** 2-3 時間で完了可能
- [x] **Straightforward Integration:** Zustand store から既存データ取得のみ
- [x] **Existing Patterns:** Ant Design Tabs/Table/Statistic パターン使用
- [x] **No Design Work:** UI デザイン確定済み

### Clarity Check

- [x] **Unambiguous Requirements:** AC に具体的な表示内容明記
- [x] **Clear Integration Points:** ResultPanel.tsx, useVRPStore.ts 明確
- [x] **Testable Criteria:** 手動テストで全データ確認可能
- [x] **Simple Rollback:** ファイル削除 + Tab エントリ削除のみ

---

## Success Criteria

Story 4.2 の成功基準:

1. ✅ 「方案対比」タブが ResultPanel に表示される
2. ✅ 4 つの総合比較指標（距離、コスト、積載率、車両）が正確に表示される
3. ✅ 改善/悪化の色分けが正確（緑=改善、赤=悪化）
4. ✅ ルート別詳細比較テーブルが正確に表示される
5. ✅ 基線方案説明アラートが表示される
6. ✅ 既存 3 タブが正常動作する（リグレッションなし）
7. ✅ TypeScript/ESLint エラーなし
8. ✅ クライアントに見せて最適化の価値が直感的に理解できる

---

**Created by:** Product Manager (John)
**Reviewed by:** Pending
**Status:** Ready for Development
**Next:** Story 4.3 - ルート方向矢印可視化
