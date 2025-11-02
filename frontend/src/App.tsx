/**
 * AI自動配車システム - メインアプリケーション
 *
 * React アプリケーションのルートコンポーネント
 */

import React from 'react';
import { ConfigProvider } from 'antd';
import jaJP from 'antd/locale/ja_JP';
import { AppLayout } from './components/Layout/AppLayout';
import { ControlPanel } from './components/Control/ControlPanel';
import { MapView } from './components/Map/MapView';
import { ResultPanel } from './components/Result/ResultPanel';
import { useVRPStore } from './stores/useVRPStore';

function App() {
  const { optimizationResult } = useVRPStore();

  return (
    <ConfigProvider locale={jaJP}>
      <AppLayout sider={<ControlPanel />}>
        {/* 地図表示エリア */}
        <MapView />

        {/* 最適化結果パネル（結果がある場合のみ表示） */}
        {optimizationResult && <ResultPanel />}
      </AppLayout>
    </ConfigProvider>
  );
}

export default App;
