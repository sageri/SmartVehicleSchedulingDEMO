/**
 * AI自動配車システム - 操作パネル（Sider）
 *
 * 左側サイドバーの操作コントロール
 */

import React from 'react';
import { Button, Divider, Typography, Space } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import { useVRPStore } from '../../stores/useVRPStore';

const { Title, Text } = Typography;

/**
 * 操作パネルコンポーネント（サイドバー内容）
 */
export const ControlPanel: React.FC = () => {
  const {
    loading,
    error,
    initDemoData,
    runOptimization,
    selectedDepotIds,
    selectedVehicleIds,
    selectedDeliveryIds,
  } = useVRPStore();

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* データ初期化セクション */}
      <div>
        <Title level={5}>1. データ初期化</Title>
        <Button
          type="primary"
          block
          icon={<ThunderboltOutlined />}
          onClick={initDemoData}
          loading={loading}
        >
          デモデータ作成
        </Button>
        <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
          拠点1件、車両3台、配送先20件を生成
        </Text>
      </div>

      <Divider />

      {/* 選択サマリー */}
      <div>
        <Title level={5}>2. 選択状態</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>拠点: {selectedDepotIds.length} 件</Text>
          <Text>車両: {selectedVehicleIds.length} 台</Text>
          <Text>配送先: {selectedDeliveryIds.length} 件</Text>
        </Space>
      </div>

      <Divider />

      {/* 最適化実行 */}
      <div>
        <Title level={5}>3. 最適化実行</Title>
        <Button
          type="primary"
          size="large"
          block
          onClick={runOptimization}
          loading={loading}
          disabled={
            selectedDepotIds.length === 0 ||
            selectedVehicleIds.length === 0 ||
            selectedDeliveryIds.length === 0
          }
        >
          VRP最適化実行
        </Button>
        <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
          計算時間: 2-30秒
        </Text>
      </div>

      {/* エラー表示 */}
      {error && (
        <>
          <Divider />
          <Text type="danger">{error}</Text>
        </>
      )}
    </Space>
  );
};
