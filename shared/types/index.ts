/**
 * AI自動配車システムデモプロトタイプ - 共有型定義
 *
 * このファイルには、フロントエンドとバックエンド間で共有される
 * すべてのTypeScript型定義が含まれています。
 *
 * Story 002決定: 同期REST API採用のため、非同期タスク関連の型は削除済み
 * - 最適化リクエストは同期実行（2-5秒で即座に結果を返す）
 * - アルゴリズムとストラテジーは固定（OR-Tools CVRPTW + 距離最適化）
 *
 * 出典: docs/architecture.md - Data Models セクション
 *       docs/decision-story002-api-algorithm.md - 技術決定
 */

// ========================================
// 基本型定義
// ========================================

export type VehicleType = "2t" | "4t"
export type TimeWindow = "morning" | "afternoon" | null

// ========================================
// データモデル
// ========================================

/**
 * 集荷拠点
 */
export interface Depot {
  id: string
  name: string
  latitude: number
  longitude: number
  address: string
  operating_hours: {
    start_time: string // HH:MM形式
    end_time: string
  }
}

/**
 * 車両
 */
export interface Vehicle {
  id: string
  vehicle_type: VehicleType
  capacity_weight: number // kg
  capacity_volume: number // m³
  depot_id: string
  available_hours: {
    start_time: string // HH:MM
    end_time: string
  }
  cost_per_km: number // ¥/km
  cost_per_hour: number // ¥/hour
}

/**
 * 配送先
 */
export interface Delivery {
  id: string
  customer_name: string
  latitude: number
  longitude: number
  address: string
  package_count: number // 1-3
  weight: number // kg
  volume: number // m³
  time_window: TimeWindow
  service_time: number // minutes
}

/**
 * ルート停車地点
 */
export interface RouteStop {
  delivery_id: string
  sequence: number // 停車順序
  arrival_time: string // ISO 8601
  departure_time: string
  distance_from_previous: number // km
  duration_from_previous: number // minutes
}

/**
 * 配送ルート
 */
export interface Route {
  id: string
  vehicle_id: string
  depot_id: string
  stops: RouteStop[]
  total_distance: number // km
  total_duration: number // minutes
  total_weight: number // kg
  total_volume: number // m³
  total_cost: number // ¥
  utilization_weight: number // 0-100%
  utilization_volume: number // 0-100%
}

/**
 * 基線メトリクス（最適化前の基準値）
 */
export interface BaselineMetrics {
  total_distance: number // 基線総距離（貪欲法または単純割当）
  total_duration: number // 基線総時間
  total_cost: number // 基線総コスト
  average_utilization_weight: number // 基線平均積載率
  method: string // 基線計算方法（"greedy" | "simple_assignment"）
}

/**
 * 改善メトリクス（最適化による削減効果）
 */
export interface ImprovementMetrics {
  distance_reduction_km: number // 距離削減（km）
  distance_reduction_percent: number // 距離削減率（%）
  duration_reduction_minutes: number // 時間削減（分）
  cost_reduction_amount: number // コスト削減金額（¥）
  cost_reduction_percent: number // コスト削減率（%）
  utilization_improvement_percent: number // 積載率改善（%）
}

/**
 * 最適化リクエスト（同期API - 簡略版）
 *
 * Story 002決定: 同期REST APIのため、最小限のパラメータのみ
 * - アルゴリズム: OR-Tools CVRPTW固定
 * - 最適化戦略: 距離最適化固定
 */
export interface OptimizationRequest {
  depot_ids: string[]
  vehicle_ids: string[]
  delivery_ids: string[]
}

/**
 * 最適化結果
 */
export interface OptimizationResult {
  id: string
  request_id: string
  routes: Route[]
  total_distance: number // km
  total_duration: number // minutes
  total_cost: number // ¥
  average_utilization_weight: number // %
  average_utilization_volume: number // %
  computation_time: number // ms
  unassigned_deliveries: string[] // delivery IDs
  baseline_metrics: BaselineMetrics // 基線指標
  improvement_metrics: ImprovementMetrics // 改善指標
  created_at: string // ISO 8601
}

// ========================================
// エクスポート
// ========================================

export type {
  // すべてのインターフェースは上記でexportされている
}
