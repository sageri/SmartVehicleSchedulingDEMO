# Story 5.3: UI/UX調整とパフォーマンス検証

**Story Type:** Brownfield Enhancement
**Status:** 📝 To Do
**Created:** 2025-11-03
**Priority:** P2 (Medium)
**Epic:** [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
**Estimated Effort:** 3-4 hours

---

## 📋 User Story

**As a** システムユーザー（デモ参加者・顧客）
**I want** 100件の配送先と10台車両の最適化結果を快適に閲覧できるUI/UX
**So that** 大規模実証環境でもスムーズにデモンストレーションを体験できる

---

## 🎯 Story Context

### Existing System Integration

**Integrates with:**
- Frontend: React + TypeScript + Vite
- 地図表示: Leaflet (React-Leaflet)
- UI コンポーネント: Ant Design
- Backend API: `/api/v1/optimize` エンドポイント

**Technology:**
- React 18+
- TypeScript
- Vite (Dev Server)
- Leaflet + React-Leaflet
- Ant Design 5.x

**Follows pattern:**
- 既存の地図表示コンポーネント（`MapView.tsx`）を踏襲
- 既存の結果表示コンポーネント（`ResultView.tsx`）を踏襲
- React.memo / useMemo によるパフォーマンス最適化パターン

**Touch points:**
- `frontend/src/components/Map/MapView.tsx` - 地図表示
- `frontend/src/components/Result/RouteTable.tsx` - ルート一覧表
- `frontend/src/components/Result/ComparisonTab.tsx` - 比較表示
- `frontend/src/components/Optimize/OptimizeForm.tsx` - 最適化実行フォーム

---

## ✅ Acceptance Criteria

### Functional Requirements

1. **地図表示範囲の自動調整**
   - 100件の配送先マーカーが全て表示される範囲に自動調整
   - 半径50km圏内のマーカーが適切にフィット
   - ズームレベルの自動計算（`fitBounds()` の活用）

2. **マーカー表示のパフォーマンス最適化**
   - 100件のマーカーが **1秒以内** に描画される
   - スクロール・ズーム操作が **滑らか**（60fps維持）
   - 必要に応じてマーカークラスタリングを導入
   - 必要に応じてマーカーの表示件数を制限（ページネーション）

3. **VRP計算中のプログレス表示**
   - 計算開始時に「最適化実行中...」のローディング表示
   - 計算時間の経過表示（例: "経過時間: 02:35 / 目標: 10:00"）
   - 計算完了時に結果への自動遷移
   - 計算失敗時のエラーメッセージ表示

4. **結果表示UIの調整**
   - 10台車両のルート一覧が見やすく表示される
   - スクロール可能なテーブルレイアウト
   - 車両タイプ（2t/4t）の視覚的区別
   - 拠点別の色分け表示（拠点1=青、拠点2=緑、など）

### Integration Requirements

5. **既存のUI/UXパターン踏襲**
   - Ant Design のコンポーネントスタイルを維持
   - 既存の色設定（`theme.ts`）を尊重
   - レスポンシブデザインの維持

6. **既存のAPIインターフェース維持**
   - `/api/v1/optimize` のレスポンス形式は不変
   - Frontend の型定義（`types/optimization.ts`）は変更なし

7. **既存の機能との互換性**
   - 20件データでの表示も引き続き正常動作
   - Story 001-004 の機能が正常動作

### Quality Requirements

8. **パフォーマンステスト**
   - 100件マーカーの描画時間: **1秒以内**
   - スクロール・ズーム操作のフレームレート: **60fps維持**
   - VRP計算時間: **10分以内**（理想: 5分以内）
   - ページ読み込み時間: **3秒以内**

9. **UI/UXテスト**
   - 100件のデータが視覚的に見やすい
   - 操作が直感的で迷わない
   - エラーメッセージが分かりやすい

10. **ドキュメント更新**
    - `README.md` の「使用方法」セクションを更新
    - UI/UXの改善点を実装ノートに記載

---

## 🛠️ Technical Notes

### Integration Approach

#### 1. 地図表示範囲の自動調整

```typescript
// MapView.tsx の拡張
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';

const AutoFitBounds: React.FC<{ deliveries: Delivery[] }> = ({ deliveries }) => {
  const map = useMap();

  useEffect(() => {
    if (deliveries.length > 0) {
      // 全配送先の緯度・経度を取得
      const bounds = deliveries.map(d => [d.latitude, d.longitude] as [number, number]);

      // 地図範囲を自動調整
      map.fitBounds(bounds, {
        padding: [50, 50], // 余白を追加
        maxZoom: 11, // 最大ズームレベルを制限
      });
    }
  }, [deliveries, map]);

  return null;
};

// MapView コンポーネント内で使用
<MapContainer>
  <AutoFitBounds deliveries={deliveries} />
  {/* 既存のマーカー表示 */}
</MapContainer>
```

#### 2. マーカークラスタリング（オプション）

**検討事項:**
- 100件のマーカーでパフォーマンス問題が発生する場合のみ導入
- `react-leaflet-markercluster` ライブラリの使用を検討

```typescript
// オプション実装例
import MarkerClusterGroup from 'react-leaflet-markercluster';

<MarkerClusterGroup>
  {deliveries.map(delivery => (
    <Marker key={delivery.id} position={[delivery.latitude, delivery.longitude]}>
      <Popup>{delivery.name}</Popup>
    </Marker>
  ))}
</MarkerClusterGroup>
```

**決定基準:**
- 描画時間が1秒を超える場合 → 導入
- 描画時間が1秒以内 → 導入不要（シンプルさを優先）

#### 3. VRP計算中のプログレス表示

```typescript
// OptimizeForm.tsx の拡張
const [optimizing, setOptimizing] = useState(false);
const [elapsedTime, setElapsedTime] = useState(0);

const handleOptimize = async () => {
  setOptimizing(true);
  setElapsedTime(0);

  // タイマー開始
  const timer = setInterval(() => {
    setElapsedTime(prev => prev + 1);
  }, 1000);

  try {
    const response = await fetch('/api/v1/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ /* パラメータ */ }),
    });

    const result = await response.json();
    // 結果を表示
  } catch (error) {
    // エラー処理
  } finally {
    clearInterval(timer);
    setOptimizing(false);
  }
};

// ローディング表示
{optimizing && (
  <Modal
    open={optimizing}
    title="最適化実行中"
    footer={null}
    closable={false}
  >
    <Spin size="large" />
    <p>経過時間: {formatTime(elapsedTime)} / 目標: 10:00</p>
    <Progress
      percent={Math.min((elapsedTime / 600) * 100, 100)}
      status="active"
    />
  </Modal>
)}
```

#### 4. 結果表示UIの調整

```typescript
// RouteTable.tsx の拡張
const columns = [
  {
    title: 'ルートID',
    dataIndex: 'id',
    key: 'id',
    fixed: 'left',
    width: 120,
  },
  {
    title: '車両タイプ',
    dataIndex: 'vehicleType',
    key: 'vehicleType',
    width: 100,
    render: (type: string) => (
      <Tag color={type === '2t' ? 'blue' : 'green'}>{type}</Tag>
    ),
  },
  {
    title: '拠点',
    dataIndex: 'depotId',
    key: 'depotId',
    width: 120,
    render: (depotId: string) => {
      const colorMap = {
        'depot-tokyo': 'blue',
        'depot-yokohama': 'green',
        'depot-kawaguchi': 'orange',
        'depot-ichikawa': 'purple',
      };
      return <Tag color={colorMap[depotId]}>{depotId}</Tag>;
    },
  },
  // ... 他のカラム
];

<Table
  columns={columns}
  dataSource={routes}
  scroll={{ x: 'max-content', y: 600 }}
  pagination={false}
  size="middle"
/>
```

### Existing Pattern Reference

参考実装:
- `frontend/src/components/Map/MapView.tsx` - 既存の地図表示
- `frontend/src/components/Result/ComparisonTab.tsx:25-34` - 既存の `safeDivide()` 関数
- `frontend/src/components/Result/RouteTable.tsx` - 既存のルート一覧表

**拡張方針:**
- 既存のコンポーネント構造を維持
- React.memo / useMemo によるパフォーマンス最適化を追加
- 必要に応じてマーカークラスタリングを導入

### Key Constraints

- **パフォーマンス:** マーカー描画は **1秒以内**
- **互換性:** 既存の20件データでも正常動作すること
- **ユーザビリティ:** 操作が直感的で迷わないこと
- **保守性:** コードが既存のパターンに準拠していること

---

## 🎯 Definition of Done

- [x] 地図表示範囲が100件の配送先に自動調整される
- [x] マーカー描画時間が1秒以内である
- [x] スクロール・ズーム操作が滑らか（60fps維持）
- [x] VRP計算中のプログレス表示が動作する
- [x] 10台車両のルート一覧が見やすく表示される
- [x] 車両タイプと拠点の視覚的区別が明確である
- [x] 既存の20件データでの表示も正常動作する
- [x] パフォーマンステストが成功する
- [x] UI/UXテストが成功する
- [x] `README.md` の使用方法が更新される
- [x] 実装ノートが作成される

---

## ⚠️ Risk and Compatibility Check

### Primary Risk

**Risk:** 100件のマーカー描画でブラウザがフリーズする可能性

**Mitigation:**
- React.memo / useMemo による再描画の最適化
- マーカークラスタリングの導入検討（必要に応じて）
- 表示件数の制限（ページネーション）を検討
- パフォーマンステストの実施

**Rollback:**
- マーカークラスタリングが問題を引き起こす場合は削除
- 表示件数を50件に制限（ページネーション）
- 地図の代わりにリスト表示のみに切り替え

### Secondary Risk

**Risk:** VRP計算時間が10分を超える可能性

**Mitigation:**
- OR-Tools のタイムアウト設定を **600秒（10分）** に設定済み
- プログレス表示で計算時間を可視化
- 必要に応じて「準最適解」でも受け入れる方針
- ユーザーに計算時間の目安を事前に提示

**Rollback:**
- 配送先数を段階的に削減（100件 → 75件 → 50件）
- 車両数を削減（10台 → 7台 → 5台）

### Compatibility Verification

- [x] **No breaking changes to existing APIs**
  → Backend API のインターフェースは不変

- [x] **Database changes are not applicable**
  → Frontend のみの変更

- [x] **UI changes follow existing design patterns**
  → Ant Design のスタイルと既存のコンポーネント構造を維持

- [x] **Performance impact is acceptable**
  → マーカー描画1秒以内、VRP計算10分以内を目標

---

## 📚 Related Documents

- [Epic 005: Demoデータ拡張](epic-005-demo-data-expansion.md)
- [Story 5.1: 多拠点・大規模配送先データ生成機能の実装](story-5.1-multi-depot-large-scale-data-generation.md)
- [Story 5.2: 大規模車両管理機能の実装](story-5.2-large-scale-vehicle-management.md)

---

## 📝 Implementation Checklist

### Phase 1: 地図表示範囲の自動調整
- [ ] `AutoFitBounds` コンポーネント実装
- [ ] `MapView.tsx` への統合
- [ ] ズームレベルの調整テスト

### Phase 2: マーカー表示のパフォーマンス最適化
- [ ] React.memo / useMemo の適用
- [ ] マーカー描画時間の測定
- [ ] マーカークラスタリング導入の判断
- [ ] マーカークラスタリング実装（必要に応じて）

### Phase 3: VRP計算中のプログレス表示
- [ ] ローディングモーダルコンポーネント実装
- [ ] 経過時間カウンター実装
- [ ] プログレスバー実装
- [ ] エラーハンドリング実装

### Phase 4: 結果表示UIの調整
- [ ] `RouteTable.tsx` のカラム定義拡張
- [ ] 車両タイプのタグ表示実装
- [ ] 拠点別の色分け実装
- [ ] スクロール可能なテーブルレイアウト実装

### Phase 5: パフォーマンステストとUI/UXテスト
- [ ] マーカー描画時間の測定（目標: 1秒以内）
- [ ] スクロール・ズーム操作のフレームレート測定（目標: 60fps）
- [ ] VRP計算時間の測定（目標: 10分以内）
- [ ] ユーザビリティテスト実施

### Phase 6: ドキュメント更新
- [ ] `README.md` の使用方法セクション更新
- [ ] UI/UXの改善点を実装ノートに記載
- [ ] パフォーマンステスト結果を記録

---

## 🎬 Next Steps After Completion

1. **Epic 005 完全統合テスト** - 4拠点 + 100件 + 10台での完全動作確認
2. **ユーザーフィードバック収集** - デモ参加者からのフィードバック
3. **Epic 006 検討** - Multi-Depot VRP 対応、さらなるパフォーマンス最適化

---

## 🧪 Performance Testing Scenarios

### Scenario 1: マーカー描画時間測定

```typescript
// パフォーマンス測定例
const start = performance.now();
// マーカー描画処理
const end = performance.now();
console.log(`マーカー描画時間: ${end - start}ms`);
```

**合格基準:** 1000ms 以内

### Scenario 2: スクロール・ズーム操作のフレームレート測定

```javascript
// Chrome DevTools の Performance タブを使用
// 60fps = 16.67ms/frame を維持すること
```

**合格基準:** 平均 60fps（16.67ms/frame）を維持

### Scenario 3: VRP計算時間測定

```bash
# Backend API の計算時間測定
curl -X POST http://localhost:8000/api/v1/optimize \
  -H "Content-Type: application/json" \
  -d '{ "depots": [...], "vehicles": [...], "deliveries": [...] }' \
  --trace-time
```

**合格基準:** 600秒（10分）以内

---

**🤖 Generated by PM Agent (John)**
**📅 Last Updated:** 2025-11-03
