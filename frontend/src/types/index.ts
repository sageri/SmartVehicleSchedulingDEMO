/**
 * AI自動配車システム - TypeScript 型定義
 *
 * Backend API (FastAPI + Pydantic) のレスポンス型定義
 * Story 002 実装済み API に基づく
 */

// ========================================
// 基本型定義
// ========================================

/** 営業時間 */
export interface OperatingHours {
  start_time: string; // "HH:MM" format
  end_time: string;   // "HH:MM" format
}

/** 時間窓 */
export type TimeWindow = 'morning' | 'afternoon' | null;

// ========================================
// データモデル
// ========================================

/**
 * 拠点（Depot）
 * 車両が出発・帰還する集荷拠点
 */
export interface Depot {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  operating_hours: OperatingHours;
}

/**
 * 車両（Vehicle）
 * 配送に使用する車両
 */
export interface Vehicle {
  id: string;
  vehicle_type: string; // "2t" | "4t"
  capacity_weight: number; // kg
  capacity_volume: number; // m³
  depot_id: string;
  available_hours: OperatingHours;
  cost_per_km: number; // ¥/km
  cost_per_hour: number; // ¥/hour
}

/**
 * 配送先（Delivery）
 * 荷物を配送する目的地
 */
export interface Delivery {
  id: string;
  customer_name: string;
  latitude: number;
  longitude: number;
  address: string;
  package_count: number;
  weight: number; // kg
  volume: number; // m³
  time_window: TimeWindow;
  service_time: number; // minutes
}

// ========================================
// VRP 最適化関連
// ========================================

/**
 * ルート停車点（Route Stop）
 * 配送ルート上の停車地点
 */
export interface RouteStop {
  delivery_id: string;
  sequence: number; // 停車順序
  arrival_time: string; // ISO 8601 format
  departure_time: string; // ISO 8601 format
  distance_from_previous: number; // km
  duration_from_previous: number; // minutes
}

/**
 * ルート（Route）
 * 1台の車両の配送経路
 */
export interface Route {
  id: string;
  vehicle_id: string;
  depot_id: string;
  stops: RouteStop[];
  total_distance: number; // km
  total_duration: number; // minutes
  total_weight: number; // kg
  total_volume: number; // m³
  total_cost: number; // ¥
  utilization_weight: number; // %
  utilization_volume: number; // %
}

/**
 * 基線指標（Baseline Metrics）
 * 最適化前の単純割当法による指標
 */
export interface BaselineMetrics {
  total_distance: number; // km
  total_duration: number; // minutes
  total_cost: number; // ¥
  average_utilization_weight: number; // %
  method: string; // "simple_assignment"
}

/**
 * 改善指標（Improvement Metrics）
 * 最適化前後の改善効果
 */
export interface ImprovementMetrics {
  distance_reduction_km: number; // km
  distance_reduction_percent: number; // %
  duration_reduction_minutes: number; // minutes
  cost_reduction_amount: number; // ¥
  cost_reduction_percent: number; // %
  utilization_improvement_percent: number; // %
}

/**
 * 最適化結果（Optimization Result）
 * VRP 最適化の完全な結果
 */
export interface OptimizationResult {
  id: string;
  request_id: string;
  routes: Route[];
  total_distance: number; // km
  total_duration: number; // minutes
  total_cost: number; // ¥
  average_utilization_weight: number; // %
  average_utilization_volume: number; // %
  computation_time: number; // milliseconds
  unassigned_deliveries: string[]; // delivery IDs
  baseline_metrics: BaselineMetrics;
  improvement_metrics: ImprovementMetrics;
  created_at: string; // ISO 8601 format
}

// ========================================
// API Request/Response
// ========================================

/**
 * VRP 最適化リクエスト
 */
export interface OptimizationRequest {
  depot_ids: string[];
  vehicle_ids: string[];
  delivery_ids: string[];
}

/**
 * API リストレスポンス（Depot）
 */
export interface DepotListResponse {
  depots: Depot[];
  total: number;
}

/**
 * API リストレスポンス（Vehicle）
 */
export interface VehicleListResponse {
  vehicles: Vehicle[];
  total: number;
}

/**
 * API リストレスポンス（Delivery）
 */
export interface DeliveryListResponse {
  deliveries: Delivery[];
  total: number;
}

/**
 * メッセージレスポンス
 */
export interface MessageResponse {
  message: string;
  detail?: string;
}

/**
 * エラーレスポンス
 */
export interface ErrorResponse {
  detail: string;
}

// ========================================
// UI 状態管理
// ========================================

/**
 * 地図表示設定
 */
export interface MapViewport {
  center: [number, number]; // [latitude, longitude]
  zoom: number;
}

/**
 * 選択状態
 */
export interface SelectionState {
  selectedDepotIds: string[];
  selectedVehicleIds: string[];
  selectedDeliveryIds: string[];
}

/**
 * UI 状態
 */
export interface UIState {
  loading: boolean;
  error: string | null;
  activeRouteId: string | null; // ハイライト中のルートID
}

// ========================================
// ユーティリティ型
// ========================================

/**
 * 座標（緯度・経度）
 */
export interface Coordinates {
  latitude: number;
  longitude: number;
}

/**
 * 地図マーカー型
 */
export type MarkerType = 'depot' | 'delivery-morning' | 'delivery-afternoon' | 'delivery-anytime';

/**
 * ルート色定義
 */
export const ROUTE_COLORS = [
  '#1f77b4', // 青
  '#ff7f0e', // オレンジ
  '#2ca02c', // 緑
  '#d62728', // 赤
  '#9467bd', // 紫
  '#8c564b', // 茶
  '#e377c2', // ピンク
  '#7f7f7f', // グレー
  '#bcbd22', // 黄緑
  '#17becf', // シアン
] as const;

/**
 * マーカー色定義
 */
export const MARKER_COLORS = {
  depot: '#1890ff',           // 青（Ant Design Primary）
  'delivery-morning': '#ff4d4f',   // 赤
  'delivery-afternoon': '#ff7a45', // オレンジ
  'delivery-anytime': '#52c41a',   // 緑
} as const;
