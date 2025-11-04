/**
 * AI自動配車システム - Zustand Store
 *
 * グローバル状態管理
 * - データ（拠点、車両、配送先、最適化結果）
 * - 選択状態（選択された拠点・車両・配送先）
 * - UI状態（Loading、エラー、アクティブルート）
 */

import { create } from 'zustand';
import type {
  Depot,
  Vehicle,
  Delivery,
  OptimizationResult,
} from '../types';
import { api } from '../services/api';

// ========================================
// Store インターフェース定義
// ========================================

interface VRPStore {
  // ----------------------------------------
  // データ
  // ----------------------------------------
  depots: Depot[];
  vehicles: Vehicle[];
  deliveries: Delivery[];
  optimizationResult: OptimizationResult | null;

  // ----------------------------------------
  // 選択状態
  // ----------------------------------------
  selectedDepotIds: string[];
  selectedVehicleIds: string[];
  selectedDeliveryIds: string[];

  // ----------------------------------------
  // UI 状態
  // ----------------------------------------
  loading: boolean;
  error: string | null;
  activeRouteId: string | null; // 地図上でハイライト中のルート

  // ----------------------------------------
  // データ設定アクション
  // ----------------------------------------
  setDepots: (depots: Depot[]) => void;
  setVehicles: (vehicles: Vehicle[]) => void;
  setDeliveries: (deliveries: Delivery[]) => void;
  setOptimizationResult: (result: OptimizationResult | null) => void;

  // ----------------------------------------
  // 選択状態アクション
  // ----------------------------------------
  toggleDepot: (id: string) => void;
  toggleVehicle: (id: string) => void;
  toggleDelivery: (id: string) => void;
  selectAllVehicles: () => void;
  selectAllDeliveries: () => void;
  clearSelections: () => void;

  // ----------------------------------------
  // UI 状態アクション
  // ----------------------------------------
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setActiveRouteId: (routeId: string | null) => void;

  // ----------------------------------------
  // API 呼び出しアクション
  // ----------------------------------------
  initDemoData: () => Promise<void>;
  loadDepots: () => Promise<void>;
  loadVehicles: (depotId?: string) => Promise<void>;
  loadDeliveries: (timeWindow?: 'morning' | 'afternoon') => Promise<void>;
  runOptimization: () => Promise<void>;

  // ----------------------------------------
  // リセット
  // ----------------------------------------
  reset: () => void;
}

// ========================================
// Zustand Store 作成
// ========================================

export const useVRPStore = create<VRPStore>((set, get) => ({
  // ----------------------------------------
  // 初期状態
  // ----------------------------------------
  depots: [],
  vehicles: [],
  deliveries: [],
  optimizationResult: null,
  selectedDepotIds: [],
  selectedVehicleIds: [],
  selectedDeliveryIds: [],
  loading: false,
  error: null,
  activeRouteId: null,

  // ----------------------------------------
  // データ設定アクション
  // ----------------------------------------
  setDepots: (depots) => set({ depots }),
  setVehicles: (vehicles) => set({ vehicles }),
  setDeliveries: (deliveries) => set({ deliveries }),
  setOptimizationResult: (result) => set({ optimizationResult: result }),

  // ----------------------------------------
  // 選択状態アクション
  // ----------------------------------------
  toggleDepot: (id) =>
    set((state) => ({
      selectedDepotIds: state.selectedDepotIds.includes(id)
        ? state.selectedDepotIds.filter((i) => i !== id)
        : [...state.selectedDepotIds, id],
    })),

  toggleVehicle: (id) =>
    set((state) => ({
      selectedVehicleIds: state.selectedVehicleIds.includes(id)
        ? state.selectedVehicleIds.filter((i) => i !== id)
        : [...state.selectedVehicleIds, id],
    })),

  toggleDelivery: (id) =>
    set((state) => ({
      selectedDeliveryIds: state.selectedDeliveryIds.includes(id)
        ? state.selectedDeliveryIds.filter((i) => i !== id)
        : [...state.selectedDeliveryIds, id],
    })),

  selectAllVehicles: () =>
    set((state) => ({
      selectedVehicleIds: state.vehicles.map((v) => v.id),
    })),

  selectAllDeliveries: () =>
    set((state) => ({
      selectedDeliveryIds: state.deliveries.map((d) => d.id),
    })),

  clearSelections: () =>
    set({
      selectedDepotIds: [],
      selectedVehicleIds: [],
      selectedDeliveryIds: [],
    }),

  // ----------------------------------------
  // UI 状態アクション
  // ----------------------------------------
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setActiveRouteId: (routeId) => set({ activeRouteId: routeId }),

  // ----------------------------------------
  // API 呼び出しアクション
  // ----------------------------------------

  /**
   * デモデータ初期化
   */
  initDemoData: async () => {
    try {
      set({ loading: true, error: null });
      await api.initDemoData();

      // データ再読み込み
      await get().loadDepots();
      await get().loadVehicles();
      await get().loadDeliveries();

      // 全選択
      get().selectAllVehicles();
      get().selectAllDeliveries();

      set({ loading: false });
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : '初期化に失敗しました',
      });
    }
  },

  /**
   * 拠点リスト取得
   */
  loadDepots: async () => {
    try {
      const response = await api.getDepots();
      set({ depots: response.depots });

      // Epic 005: 拠点が存在する場合は全選択（Multi-Depot VRP対応）
      if (response.depots.length > 0) {
        set({ selectedDepotIds: response.depots.map((d) => d.id) });
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '拠点の取得に失敗しました',
      });
    }
  },

  /**
   * 車両リスト取得
   */
  loadVehicles: async (depotId?: string) => {
    try {
      const response = await api.getVehicles(depotId);
      set({ vehicles: response.vehicles });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '車両の取得に失敗しました',
      });
    }
  },

  /**
   * 配送先リスト取得
   */
  loadDeliveries: async (timeWindow?) => {
    try {
      const response = await api.getDeliveries(timeWindow);
      set({ deliveries: response.deliveries });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '配送先の取得に失敗しました',
      });
    }
  },

  /**
   * VRP 最適化実行
   */
  runOptimization: async () => {
    const state = get();

    // バリデーション
    if (state.selectedDepotIds.length === 0) {
      set({ error: '拠点を選択してください' });
      return;
    }
    if (state.selectedVehicleIds.length === 0) {
      set({ error: '車両を選択してください' });
      return;
    }
    if (state.selectedDeliveryIds.length === 0) {
      set({ error: '配送先を選択してください' });
      return;
    }

    try {
      set({ loading: true, error: null, optimizationResult: null });

      const result = await api.optimize({
        depot_ids: state.selectedDepotIds,
        vehicle_ids: state.selectedVehicleIds,
        delivery_ids: state.selectedDeliveryIds,
      });

      set({
        optimizationResult: result,
        loading: false,
      });

      console.log('[Optimization Success]', result);
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : '最適化に失敗しました',
      });
    }
  },

  // ----------------------------------------
  // リセット
  // ----------------------------------------
  reset: () =>
    set({
      optimizationResult: null,
      selectedDepotIds: [],
      selectedVehicleIds: [],
      selectedDeliveryIds: [],
      error: null,
      activeRouteId: null,
    }),
}));
