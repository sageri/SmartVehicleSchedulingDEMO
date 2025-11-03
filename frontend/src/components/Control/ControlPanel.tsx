/**
 * AI自動配車システム - 操作パネル（Sider）
 *
 * 左側サイドバーの操作コントロール
 */

import React, { useState, useEffect } from 'react';
import { Button, Divider, Typography, Space, Modal, Spin, Progress } from 'antd';
import { ThunderboltOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useVRPStore } from '../../stores/useVRPStore';
import { SelectionDetailDrawer } from './SelectionDetailDrawer';

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

  // Drawer 表示状態管理
  const [detailsVisible, setDetailsVisible] = useState(false);

  // Story 5.3: 最適化進捗表示
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // 最適化中の経過時間カウンター（Story 5.3）
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;

    if (loading) {
      setElapsedSeconds(0);
      timer = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timer) {
        clearInterval(timer);
      }
      setElapsedSeconds(0);
    }

    return () => {
      if (timer) {
        clearInterval(timer);
      }
    };
  }, [loading]);

  // 経過時間のフォーマット (mm:ss)
  const formatElapsedTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 選択データの有無チェック
  const hasSelection =
    selectedDepotIds.length > 0 ||
    selectedVehicleIds.length > 0 ||
    selectedDeliveryIds.length > 0;

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
          拠点4件、車両10台、配送先100件を生成
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

          {/* 詳細表示ボタン */}
          <Button
            size="small"
            icon={<InfoCircleOutlined />}
            onClick={() => setDetailsVisible(true)}
            disabled={!hasSelection}
            style={{ marginTop: 8 }}
          >
            詳細を表示
          </Button>
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
          計算時間: 2秒-10分（データ規模による）
        </Text>
      </div>

      {/* エラー表示 */}
      {error && (
        <>
          <Divider />
          <Text type="danger">{error}</Text>
        </>
      )}

      {/* 選択状態詳細Drawer */}
      <SelectionDetailDrawer
        visible={detailsVisible}
        onClose={() => setDetailsVisible(false)}
      />

      {/* Story 5.3: 最適化進捗モーダル */}
      <Modal
        open={loading}
        title="VRP最適化実行中"
        footer={null}
        closable={false}
        centered
        width={400}
      >
        <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }} size="large">
          <Spin size="large" />
          <div>
            <Text strong style={{ fontSize: 16 }}>
              経過時間: {formatElapsedTime(elapsedSeconds)}
            </Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>
              目標: 10:00 以内
            </Text>
          </div>
          <Progress
            percent={Math.min((elapsedSeconds / 600) * 100, 100)}
            status={elapsedSeconds >= 600 ? 'exception' : 'active'}
            strokeColor={elapsedSeconds >= 600 ? '#ff4d4f' : '#1890ff'}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            配送先数が多い場合、計算に数分かかることがあります
          </Text>
        </Space>
      </Modal>
    </Space>
  );
};
