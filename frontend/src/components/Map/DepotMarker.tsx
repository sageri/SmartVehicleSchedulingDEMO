/**
 * AI自動配車システム - 拠点マーカーコンポーネント
 *
 * 拠点を地図上に青色マーカーで表示
 */

import React from 'react';
import { Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import type { Depot } from '../../types';

// 拠点用カスタムアイコン（青色）
const depotIcon = L.divIcon({
  className: 'custom-icon',
  html: `
    <div style="
      background-color: #1890ff;
      border: 3px solid #fff;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-weight: bold;
      font-size: 18px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">
      🏢
    </div>
  `,
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

interface DepotMarkerProps {
  depot: Depot;
}

/**
 * 拠点マーカーコンポーネント
 */
export const DepotMarker: React.FC<DepotMarkerProps> = ({ depot }) => {
  return (
    <>
      {/* マーカー */}
      <Marker
        position={[depot.latitude, depot.longitude]}
        icon={depotIcon}
      >
        <Popup>
          <div style={{ minWidth: 200 }}>
            <h3 style={{ margin: 0, marginBottom: 8 }}>
              🏢 {depot.name}
            </h3>
            <p style={{ margin: '4px 0', fontSize: 12 }}>
              <strong>住所:</strong> {depot.address}
            </p>
            <p style={{ margin: '4px 0', fontSize: 12 }}>
              <strong>営業時間:</strong> {depot.operating_hours.start_time} - {depot.operating_hours.end_time}
            </p>
            <p style={{ margin: '4px 0', fontSize: 12, color: '#888' }}>
              <strong>座標:</strong> ({depot.latitude.toFixed(4)}, {depot.longitude.toFixed(4)})
            </p>
          </div>
        </Popup>
      </Marker>

      {/* 拠点周辺の円（オプション） */}
      <Circle
        center={[depot.latitude, depot.longitude]}
        radius={100}
        pathOptions={{
          color: '#1890ff',
          fillColor: '#1890ff',
          fillOpacity: 0.1,
          weight: 1,
        }}
      />
    </>
  );
};
