/**
 * AI自動配車システム - ルートポリラインコンポーネント
 *
 * 最適化されたルートを Polyline で地図上に表示
 * - 各ルートは異なる色で表示
 * - 拠点 → 配送先1 → 配送先2 → ... → 拠点
 * - Story 4.3: ルート方向矢印可視化（各セグメント中点に矢印表示）
 */

import React from 'react';
import { Polyline, Popup, Marker } from 'react-leaflet';
import { divIcon } from 'leaflet';
import type { Route, Depot, Delivery } from '../../types';
import { ROUTE_COLORS } from '../../types';

interface RoutePolylineProps {
  route: Route;
  routeIndex: number;
  depots: Depot[];
  deliveries: Delivery[];
}

/**
 * 2点間の中点と角度を計算
 * @param from 始点座標 [latitude, longitude]
 * @param to 終点座標 [latitude, longitude]
 * @returns 中点座標と角度（度数法）
 */
const calculateMidpointAndAngle = (
  from: [number, number],
  to: [number, number]
): { midpoint: [number, number]; angle: number } => {
  const midpoint: [number, number] = [
    (from[0] + to[0]) / 2,
    (from[1] + to[1]) / 2,
  ];

  // 角度計算（atan2 で北を0度、時計回りを正とする）
  const deltaLng = to[1] - from[1];
  const deltaLat = to[0] - from[0];
  const angle = Math.atan2(deltaLng, deltaLat) * (180 / Math.PI);

  return { midpoint, angle };
};

/**
 * 矢印アイコンを作成
 * @param color ルートの色
 * @param angle 回転角度（度数法）
 * @returns Leaflet DivIcon
 */
const createArrowIcon = (color: string, angle: number) => {
  return divIcon({
    html: `
      <div style="
        transform: rotate(${angle}deg);
        pointer-events: none;
      ">
        <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 0 L15 10 L10 8 L5 10 Z" fill="${color}" stroke="white" stroke-width="1"/>
        </svg>
      </div>
    `,
    className: 'route-arrow-icon',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

/**
 * ルートポリラインコンポーネント
 */
export const RoutePolyline: React.FC<RoutePolylineProps> = ({
  route,
  routeIndex,
  depots,
  deliveries,
}) => {
  // ルートの色（ローテーション）
  const routeColor = ROUTE_COLORS[routeIndex % ROUTE_COLORS.length];

  // 拠点を探す
  const depot = depots.find((d) => d.id === route.depot_id);
  if (!depot) {
    console.warn(`Depot ${route.depot_id} not found for route ${route.id}`);
    return null;
  }

  // ルートの座標配列を構築
  const coordinates: [number, number][] = [
    [depot.latitude, depot.longitude], // 拠点から出発
  ];

  // 各停車点の座標を追加
  route.stops.forEach((stop) => {
    const delivery = deliveries.find((d) => d.id === stop.delivery_id);
    if (delivery) {
      coordinates.push([delivery.latitude, delivery.longitude]);
    }
  });

  // 拠点に戻る
  coordinates.push([depot.latitude, depot.longitude]);

  // 各セグメントの矢印を計算
  const arrows = [];
  for (let i = 0; i < coordinates.length - 1; i++) {
    const from = coordinates[i];
    const to = coordinates[i + 1];
    const { midpoint, angle } = calculateMidpointAndAngle(from, to);
    arrows.push(
      <Marker
        key={`arrow-${route.id}-${i}`}
        position={midpoint}
        icon={createArrowIcon(routeColor, angle)}
        interactive={false}
        zIndexOffset={-1000} // ルート線の下に配置
      />
    );
  }

  return (
    <>
      <Polyline
      positions={coordinates}
      pathOptions={{
        color: routeColor,
        weight: 4,
        opacity: 0.7,
        lineCap: 'round',
        lineJoin: 'round',
      }}
    >
      <Popup>
        <div style={{ minWidth: 250 }}>
          <h3 style={{ margin: 0, marginBottom: 8, color: routeColor }}>
            🚛 ルート {routeIndex + 1}
          </h3>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>車両ID:</strong> {route.vehicle_id}
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>拠点:</strong> {depot.name}
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>停車数:</strong> {route.stops.length} 箇所
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>総距離:</strong> {route.total_distance.toFixed(1)} km
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>総時間:</strong> {route.total_duration} 分
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>総コスト:</strong> ¥{route.total_cost.toLocaleString()}
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>積載率:</strong>{' '}
            重量 {route.utilization_weight.toFixed(1)}%、
            体積 {route.utilization_volume.toFixed(1)}%
          </p>
          <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid #eee' }}>
            <strong style={{ fontSize: 12 }}>停車順序:</strong>
            <ol style={{ margin: '4px 0', paddingLeft: 20, fontSize: 11 }}>
              {route.stops.map((stop) => {
                const delivery = deliveries.find((d) => d.id === stop.delivery_id);
                return (
                  <li key={stop.delivery_id} style={{ marginBottom: 2 }}>
                    {delivery?.customer_name || stop.delivery_id}
                    <span style={{ color: '#888' }}>
                      {' '}({stop.distance_from_previous.toFixed(1)} km)
                    </span>
                  </li>
                );
              })}
            </ol>
          </div>
        </div>
      </Popup>
    </Polyline>

    {/* ルート方向矢印 */}
    {arrows}
  </>
  );
};
