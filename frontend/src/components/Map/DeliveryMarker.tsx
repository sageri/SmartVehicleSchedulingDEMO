/**
 * AI自動配車システム - 配送先マーカーコンポーネント
 *
 * 配送先を時間窓により色分けして表示
 * - morning: 赤色
 * - afternoon: オレンジ色
 * - anytime: 緑色
 */

import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { Delivery } from '../../types';

// 時間窓による色分け
const getMarkerColor = (timeWindow: 'morning' | 'afternoon' | null): string => {
  switch (timeWindow) {
    case 'morning':
      return '#ff4d4f'; // 赤
    case 'afternoon':
      return '#fadb14'; // 黄色（視認性向上）
    default:
      return '#52c41a'; // 緑
  }
};

// 時間窓のラベル
const getTimeWindowLabel = (timeWindow: 'morning' | 'afternoon' | null): string => {
  switch (timeWindow) {
    case 'morning':
      return '午前指定 (8:00-12:00)';
    case 'afternoon':
      return '午後指定 (13:00-18:00)';
    default:
      return '時間指定なし';
  }
};

// 配送先用カスタムアイコン生成
const createDeliveryIcon = (timeWindow: 'morning' | 'afternoon' | null) => {
  const color = getMarkerColor(timeWindow);
  return L.divIcon({
    className: 'custom-icon',
    html: `
      <div style="
        background-color: ${color};
        border: 2px solid #fff;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
      ">
        📦
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

interface DeliveryMarkerProps {
  delivery: Delivery;
}

/**
 * 配送先マーカーコンポーネント
 */
export const DeliveryMarker: React.FC<DeliveryMarkerProps> = ({ delivery }) => {
  const icon = createDeliveryIcon(delivery.time_window);

  return (
    <Marker
      position={[delivery.latitude, delivery.longitude]}
      icon={icon}
    >
      <Popup>
        <div style={{ minWidth: 220 }}>
          <h3 style={{ margin: 0, marginBottom: 8 }}>
            📦 {delivery.customer_name}
          </h3>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>住所:</strong> {delivery.address}
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>時間窓:</strong>{' '}
            <span style={{ color: getMarkerColor(delivery.time_window) }}>
              {getTimeWindowLabel(delivery.time_window)}
            </span>
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>荷物:</strong> {delivery.package_count} 個 ({delivery.weight} kg, {delivery.volume} m³)
          </p>
          <p style={{ margin: '4px 0', fontSize: 12 }}>
            <strong>サービス時間:</strong> {delivery.service_time} 分
          </p>
          <p style={{ margin: '4px 0', fontSize: 12, color: '#888' }}>
            <strong>座標:</strong> ({delivery.latitude.toFixed(4)}, {delivery.longitude.toFixed(4)})
          </p>
        </div>
      </Popup>
    </Marker>
  );
};
