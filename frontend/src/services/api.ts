/**
 * AI自動配車システム - API Client
 *
 * Backend API (FastAPI) との通信を管理する Axios ラッパー
 * Story 002 実装済み 5 エンドポイント対応
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  DepotListResponse,
  VehicleListResponse,
  DeliveryListResponse,
  MessageResponse,
  OptimizationRequest,
  OptimizationResult,
  TimeWindow,
} from '../types';

// ========================================
// API Client 設定
// ========================================

/** Backend API Base URL */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/** Axios Instance 作成 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 35000, // 30秒API + 5秒マージン
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========================================
// Axios Interceptors
// ========================================

/** リクエストインターセプター（ログ出力） */
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

/** レスポンスインターセプター（エラーハンドリング） */
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.url}`, response.data);
    return response;
  },
  (error: AxiosError) => {
    console.error('[API Response Error]', error.response?.data || error.message);

    // エラーメッセージの整形
    if (error.response) {
      // サーバーエラー（400, 422, 500 など）
      const errorData = error.response.data as any;
      const errorMessage = errorData?.detail || errorData?.message || 'サーバーエラーが発生しました';
      return Promise.reject(new Error(errorMessage));
    } else if (error.request) {
      // ネットワークエラー
      return Promise.reject(new Error('ネットワークエラー: サーバーに接続できません'));
    } else {
      // その他のエラー
      return Promise.reject(new Error(error.message || '予期しないエラーが発生しました'));
    }
  }
);

// ========================================
// API Methods
// ========================================

/**
 * API Client
 * 各エンドポイントへのアクセスを提供
 */
export const api = {
  // ========================================
  // 1. POST /api/v1/seed/demo-data
  // デモデータ初期化
  // ========================================

  /**
   * デモデータを初期化
   * 拠点1件、車両3台、配送先20件を生成
   */
  initDemoData: async (): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>('/seed/demo-data');
    return response.data;
  },

  // ========================================
  // 2. GET /api/v1/depots
  // 拠点リスト取得
  // ========================================

  /**
   * 拠点リストを取得
   */
  getDepots: async (): Promise<DepotListResponse> => {
    const response = await apiClient.get<DepotListResponse>('/depots');
    return response.data;
  },

  // ========================================
  // 3. GET /api/v1/vehicles
  // 車両リスト取得
  // ========================================

  /**
   * 車両リストを取得
   * @param depotId 拠点IDでフィルタ（オプション）
   */
  getVehicles: async (depotId?: string): Promise<VehicleListResponse> => {
    const response = await apiClient.get<VehicleListResponse>('/vehicles', {
      params: depotId ? { depot_id: depotId } : {},
    });
    return response.data;
  },

  // ========================================
  // 4. GET /api/v1/deliveries
  // 配送先リスト取得
  // ========================================

  /**
   * 配送先リストを取得
   * @param timeWindow 時間窓でフィルタ（オプション）
   */
  getDeliveries: async (timeWindow?: TimeWindow): Promise<DeliveryListResponse> => {
    const response = await apiClient.get<DeliveryListResponse>('/deliveries', {
      params: timeWindow ? { time_window: timeWindow } : {},
    });
    return response.data;
  },

  // ========================================
  // 5. POST /api/v1/optimization/optimize
  // VRP 最適化実行（同期API）
  // ========================================

  /**
   * VRP 最適化を実行（同期）
   * 2-30秒で結果が返却される
   *
   * @param request 最適化リクエスト
   * @returns 最適化結果
   */
  optimize: async (request: OptimizationRequest): Promise<OptimizationResult> => {
    const response = await apiClient.post<OptimizationResult>(
      '/optimization/optimize',
      request
    );
    return response.data;
  },
};

// ========================================
// エクスポート
// ========================================

export default api;
