/**
 * AI自動配車システム - 地図ビューコンポーネント
 *
 * Leaflet + React-Leaflet による地図表示
 * - 拠点マーカー（青）
 * - 配送先マーカー（時間窓により色分け）
 * - 最適化ルート（Polyline）
 */

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import { useVRPStore } from '../../stores/useVRPStore';
import { DepotMarker } from './DepotMarker';
import { DeliveryMarker } from './DeliveryMarker';
import { RoutePolyline } from './RoutePolyline';
import 'leaflet/dist/leaflet.css';
import type { Depot, Delivery, Route } from '../../types';

// Fix Leaflet default icon issue with Vite
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

/**
 * 地図の中心と拡大率を自動調整するコンポーネント
 */
const MapBoundsUpdater: React.FC<{
  depots: Depot[];
  deliveries: Delivery[];
}> = ({ depots, deliveries }) => {
  const map = useMap();

  useEffect(() => {
    const allPoints = [
      ...depots.map((d) => [d.latitude, d.longitude] as [number, number]),
      ...deliveries.map((d) => [d.latitude, d.longitude] as [number, number]),
    ];

    if (allPoints.length > 0) {
      const bounds = L.latLngBounds(allPoints);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [depots, deliveries, map]);

  return null;
};

/**
 * 地図ビューコンポーネント
 */
export const MapView: React.FC = () => {
  const { depots, deliveries, optimizationResult } = useVRPStore();

  // 東京中心座標
  const defaultCenter: [number, number] = [35.6812, 139.7671];
  const defaultZoom = 11;

  return (
    <div style={{ height: 'calc(100vh - 64px)', width: '100%' }}>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        {/* OpenStreetMap タイル */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 地図範囲自動調整 */}
        {(depots.length > 0 || deliveries.length > 0) && (
          <MapBoundsUpdater depots={depots} deliveries={deliveries} />
        )}

        {/* 拠点マーカー */}
        {depots.map((depot) => (
          <DepotMarker key={depot.id} depot={depot} />
        ))}

        {/* 配送先マーカー */}
        {deliveries.map((delivery) => (
          <DeliveryMarker key={delivery.id} delivery={delivery} />
        ))}

        {/* 最適化ルート（Polyline） */}
        {optimizationResult?.routes.map((route, index) => (
          <RoutePolyline
            key={route.id}
            route={route}
            routeIndex={index}
            depots={depots}
            deliveries={deliveries}
          />
        ))}
      </MapContainer>
    </div>
  );
};
