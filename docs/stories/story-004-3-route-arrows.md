# Story 4.3: ルート方向矢印可視化 - Brownfield Addition

**Parent Epic:** Story 004 - Demo展示増強
**作成日:** 2025-11-03
**優先度:** High (P0)
**予定工数:** 1 時間
**状態:** Ready for Development

---

## User Story

**As a** Demo プレゼンター（営業・PM）,
**I want** 地図上のルート線に方向矢印を表示,
**So that** クライアントに対して車両の移動方向を視覚的に明確に示すことができる。

---

## Story Context

### Existing System Integration

**統合先コンポーネント:**
- `frontend/src/components/Map/RoutePolyline.tsx` - ルート描画コンポーネント

**技術スタック:**
- React 18 + TypeScript 5
- Leaflet 1.9+ (Marker, DivIcon)
- 既存の Polyline 描画ロジック

**既存パターン:**
- Leaflet `<Polyline>` コンポーネント（ルート線描画）
- Leaflet `<Marker>` + `<DivIcon>` コンポーネント（カスタムアイコン）
- `DepotMarker.tsx` / `DeliveryMarker.tsx` の DivIcon パターン

**Touch Points:**
- `RoutePolyline.tsx`: 既存ルート描画ロジックに矢印追加
- Zustand store: データ取得のみ（変更なし）

**現在の実装:**
- 各ルートが色分けされた Polyline で表示される（10色ローテーション）
- クリックでハイライト表示
- 方向情報は視覚的に示されていない（ユーザーはルート開始・終了が不明確）

---

## Acceptance Criteria

### Functional Requirements

**1. ルート中点への矢印配置**
- 各ルートの Polyline 中点位置に方向矢印を 1 個配置
- 矢印は車両の移動方向（拠点 → 配送先 → 拠点）を指す
- 矢印色はルート Polyline の色と同一

**2. 矢印の視覚デザイン**

```
矢印仕様:
- 形状: ▶（三角形、右向き）
- サイズ: 20px × 20px
- 色: ルート色と同一（例: route-1 は赤、route-2 は青）
- 背景: 白色の円形背景（直径 30px）+ 影効果
- 回転: ルート進行方向に合わせて自動回転
```

**視覚例:**
```
拠点 ●━━━━━━━▶━━━━━━━● 配送先
       (矢印はルート中点に配置、進行方向を指す)
```

**3. 矢印の回転角度計算**

- ルート座標配列の中点を取得（`coordinates[midIndex]`）
- 中点前後の 2 点を使用して方向角度を計算:
  ```typescript
  const angle = Math.atan2(
    nextPoint.lat - prevPoint.lat,
    nextPoint.lng - prevPoint.lng
  ) * (180 / Math.PI);
  ```
- CSS `transform: rotate(${angle}deg)` で矢印を回転

**4. 複数ルート対応**
- 全ルートに矢印を自動配置
- 各ルートの色に合わせて矢印色を変更
- ルート選択時（ハイライト）も矢印が追従して強調表示

**5. インタラクション**
- 矢印はクリック不可（`pointer-events: none`）
- 矢印の下の Polyline はクリック可能（ルート選択機能を維持）
- 地図ズーム時も矢印サイズは固定（CSS px 単位）

### Integration Requirements

**6. 既存機能の保持**
- Polyline の既存機能（クリック選択、ハイライト）が正常動作
- Marker（拠点・配送先）の表示に影響なし
- 地図のパン・ズーム操作が正常動作

**7. 既存パターンの踏襲**
- Leaflet `<Marker>` + `<DivIcon>` パターンを使用
- `DepotMarker.tsx` / `DeliveryMarker.tsx` と同様の実装スタイル
- TypeScript strict mode 準拠

**8. 統合動作**
- ルート表示/非表示切り替え時に矢印も同期
- 新規最適化実行時に矢印が再計算・再描画される

### Quality Requirements

**9. コード品質**
- TypeScript エラー: 0件
- ESLint 警告: 0件
- `RoutePolyline.tsx` のみ修正（新規ファイル不要）

**10. パフォーマンス**
- 矢印計算は O(1)（各ルートに 1 個のみ）
- レンダリングコスト: 無視できるレベル（最大 10 ルート = 10 矢印）

**11. テスト**
- 手動テスト: 全ルートに矢印が表示され、方向が正確
- リグレッションテスト: 既存のルート選択機能が正常動作

**12. ドキュメント**
- コンポーネント内に JSDoc コメント追加
- Story 完了後、`story-004-3-completion-report.md` 作成

---

## Technical Notes

### Implementation Approach

**修正ファイル:**
```
frontend/src/components/Map/RoutePolyline.tsx
```

**実装ステップ:**

**Step 1: 中点位置と角度計算ロジック**

```typescript
/**
 * ルート座標配列から中点位置と方向角度を計算
 */
const calculateMidpointAndAngle = (
  coordinates: [number, number][]
): { position: [number, number]; angle: number } | null => {
  if (coordinates.length < 2) return null;

  const midIndex = Math.floor(coordinates.length / 2);
  const midPoint = coordinates[midIndex];

  // 前後の点を取得（角度計算用）
  const prevIndex = Math.max(0, midIndex - 1);
  const nextIndex = Math.min(coordinates.length - 1, midIndex + 1);

  const prevPoint = coordinates[prevIndex];
  const nextPoint = coordinates[nextIndex];

  // 角度計算（ラジアン → 度）
  const angle = Math.atan2(
    nextPoint[0] - prevPoint[0], // lat 差分
    nextPoint[1] - prevPoint[1]  // lng 差分
  ) * (180 / Math.PI);

  return {
    position: midPoint,
    angle: angle,
  };
};
```

**Step 2: RoutePolyline.tsx 修正**

```tsx
import { Polyline, Marker } from 'react-leaflet';
import { divIcon } from 'leaflet';
import { useVRPStore } from '@/stores/useVRPStore';

interface RoutePolylineProps {
  route: Route;
  color: string;
  isActive: boolean;
  onClick: () => void;
}

/**
 * ルート線と方向矢印を表示するコンポーネント
 *
 * 各ルートの Polyline 上に方向矢印を配置し、車両の移動方向を視覚化します。
 */
export const RoutePolyline: React.FC<RoutePolylineProps> = ({
  route,
  color,
  isActive,
  onClick,
}) => {
  // ルート座標を取得
  const coordinates = route.stops.map(stop => {
    const delivery = /* ... 既存ロジック ... */;
    return [delivery.latitude, delivery.longitude] as [number, number];
  });

  // 拠点座標を追加（開始・終了）
  const depot = /* ... 既存ロジック ... */;
  const fullCoordinates = [
    [depot.latitude, depot.longitude],
    ...coordinates,
    [depot.latitude, depot.longitude],
  ];

  // 中点位置と角度を計算
  const arrowData = calculateMidpointAndAngle(fullCoordinates);

  // 矢印アイコン生成
  const createArrowIcon = (angle: number, color: string) => {
    return divIcon({
      html: `
        <div style="
          width: 30px;
          height: 30px;
          background: white;
          border-radius: 50%;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          transform: rotate(${angle}deg);
        ">
          <div style="
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 12px solid ${color};
            transform: rotate(90deg);
          "></div>
        </div>
      `,
      className: 'route-arrow-icon',
      iconSize: [30, 30],
      iconAnchor: [15, 15],
    });
  };

  return (
    <>
      {/* 既存の Polyline */}
      <Polyline
        positions={fullCoordinates}
        pathOptions={{
          color: color,
          weight: isActive ? 5 : 3,
          opacity: isActive ? 1 : 0.7,
        }}
        eventHandlers={{ click: onClick }}
      />

      {/* 方向矢印 */}
      {arrowData && (
        <Marker
          position={arrowData.position}
          icon={createArrowIcon(arrowData.angle, color)}
          interactive={false}  // クリック不可
        />
      )}
    </>
  );
};
```

**Step 3: CSS スタイル追加（オプション）**

`App.css` または `index.css` に追加：

```css
/* ルート矢印アイコン */
.route-arrow-icon {
  pointer-events: none; /* クリック無効化 */
  transition: transform 0.2s ease; /* アニメーション（オプション） */
}
```

### Alternative Implementation (Decorator Pattern)

Leaflet の `polylineDecorator` ライブラリを使用する方法もあるが、以下の理由で非推奨：

**非推奨理由:**
1. **新規依存関係が必要:**
   - `leaflet-polylinedecorator` パッケージのインストール必要
   - Story 004 の制約（Zero New Dependencies）に違反

2. **実装時間が増加:**
   - ライブラリの調査・統合に 1-2 時間追加必要
   - 現在のアプローチは 1 時間で完了可能

3. **カスタマイズ性の低下:**
   - 矢印スタイルのカスタマイズが制限される
   - ルート色との同期が複雑化

**結論:** 上記の DivIcon アプローチを採用（シンプル、依存関係なし、1時間で完了）

### Key Constraints

- **Zero New Dependencies:** 既存ライブラリのみ使用
- **Zero Backend Changes:** Frontend のみの実装
- **Minimal Code Impact:** RoutePolyline.tsx のみ修正
- **Desktop Only:** レスポンシブ対応不要（1920×1080 想定）

---

## Definition of Done

### 完了チェックリスト

- [ ] **機能実装完了**
  - [ ] RoutePolyline.tsx に矢印計算ロジック追加
  - [ ] 中点位置計算ロジック実装
  - [ ] 角度計算ロジック実装（Math.atan2）
  - [ ] DivIcon による矢印アイコン生成

- [ ] **視覚表示正確性**
  - [ ] 全ルートに矢印が表示される
  - [ ] 矢印の方向がルート進行方向と一致
  - [ ] 矢印色がルート Polyline 色と一致
  - [ ] 矢印の背景（白円 + 影）が正常表示

- [ ] **統合要件**
  - [ ] 既存のルート選択機能が正常動作
  - [ ] 矢印がクリック不可（Polyline は引き続きクリック可能）
  - [ ] 地図ズーム時に矢印サイズが固定

- [ ] **コード品質**
  - [ ] TypeScript エラー: 0件
  - [ ] ESLint 警告: 0件
  - [ ] JSDoc コメント追加

- [ ] **テスト**
  - [ ] 手動テスト: 全ルートに矢印が表示され、方向が正確
  - [ ] リグレッションテスト: 既存のルート機能が正常動作

- [ ] **ドキュメント**
  - [ ] `story-004-3-completion-report.md` 作成
  - [ ] コード内コメント完備

---

## Risk and Compatibility Check

### Minimal Risk Assessment

**Primary Risk:**
RoutePolyline.tsx 修正による既存ルート表示機能への影響

**Mitigation:**
- 矢印は独立した Marker として実装、Polyline ロジック不変
- `interactive={false}` で矢印のクリックを無効化、Polyline のクリック機能を保持
- 計算ロジックは純粋関数（副作用なし）

**Rollback:**
- `calculateMidpointAndAngle` 関数を削除
- RoutePolyline.tsx の矢印 Marker コードブロックを削除
- 3分以内でロールバック可能

### Compatibility Verification

- [x] **No Breaking Changes:** 既存 API 不変
- [x] **Database:** 変更なし
- [x] **UI Patterns:** Leaflet Marker + DivIcon パターン踏襲
- [x] **Performance:** 影響なし（計算量 O(n)、n は最大 10 ルート）

---

## Validation Checklist

### Scope Validation

- [x] **Single Session:** 1 時間で完了可能
- [x] **Straightforward Integration:** 既存 RoutePolyline.tsx に矢印ロジック追加のみ
- [x] **Existing Patterns:** Leaflet Marker + DivIcon パターン使用
- [x] **No Design Work:** UI デザイン確定済み

### Clarity Check

- [x] **Unambiguous Requirements:** AC に矢印の位置・サイズ・色明記
- [x] **Clear Integration Points:** RoutePolyline.tsx のみ修正
- [x] **Testable Criteria:** 手動テストで全ルートの矢印確認可能
- [x] **Simple Rollback:** コードブロック削除のみ

---

## Success Criteria

Story 4.3 の成功基準:

1. ✅ 全ルートに方向矢印が中点位置に表示される
2. ✅ 矢印の方向がルート進行方向と一致する
3. ✅ 矢印色がルート Polyline 色と一致する
4. ✅ 矢印がクリック不可、Polyline のクリック機能が正常動作
5. ✅ 既存のルート選択機能が正常動作する
6. ✅ TypeScript/ESLint エラーなし
7. ✅ クライアントに見せてルート方向が直感的に理解できる

---

**Created by:** Product Manager (John)
**Reviewed by:** Pending
**Status:** Ready for Development
**Next:** Story 004 実装フェーズ開始
