/**
 * AI自動配車システム - 選択状態詳細Drawer
 *
 * 選択された拠点・車両・配送先の詳細データを表示
 * Story 4.1: 選択状態詳細情報表示
 */

import React, { useMemo } from 'react';
import { Drawer, Descriptions, Table, Typography, Space, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useVRPStore } from '../../stores/useVRPStore';
import type { Vehicle, Delivery } from '../../types';

const { Title, Text } = Typography;

interface SelectionDetailDrawerProps {
  visible: boolean;
  onClose: () => void;
}

/**
 * 選択状態詳細Drawerコンポーネント
 *
 * 選択された拠点・車両・配送先の詳細情報を表示します。
 * - 拠点詳細: ID、名称、住所、座標、営業時間
 * - 車両詳細: テーブル形式で車両スペック一覧
 * - 配送先詳細: テーブル形式（ページネーション付き）、時間窓でソート
 */
export const SelectionDetailDrawer: React.FC<SelectionDetailDrawerProps> = ({
  visible,
  onClose,
}) => {
  const {
    depots,
    vehicles,
    deliveries,
    selectedDepotIds,
    selectedVehicleIds,
    selectedDeliveryIds,
  } = useVRPStore();

  // 選択されたデータをフィルタ
  const selectedDepots = useMemo(
    () => depots.filter((d) => selectedDepotIds.includes(d.id)),
    [depots, selectedDepotIds]
  );

  const selectedVehicles = useMemo(
    () => vehicles.filter((v) => selectedVehicleIds.includes(v.id)),
    [vehicles, selectedVehicleIds]
  );

  const selectedDeliveries = useMemo(
    () => deliveries.filter((d) => selectedDeliveryIds.includes(d.id)),
    [deliveries, selectedDeliveryIds]
  );

  // ✅ 決定事項: 配送先を時間窓でソート（morning → afternoon → anytime）
  const sortedDeliveries = useMemo(() => {
    const timeWindowOrder: Record<string, number> = {
      morning: 1,
      afternoon: 2,
      anytime: 3,
    };

    return [...selectedDeliveries].sort((a, b) => {
      const orderA = timeWindowOrder[a.time_window || 'anytime'];
      const orderB = timeWindowOrder[b.time_window || 'anytime'];
      return orderA - orderB;
    });
  }, [selectedDeliveries]);

  // 総容量計算（車両）
  const totalCapacity = useMemo(() => {
    const weight = selectedVehicles.reduce((sum, v) => sum + v.capacity_weight, 0);
    const volume = selectedVehicles.reduce((sum, v) => sum + v.capacity_volume, 0);
    return { weight, volume };
  }, [selectedVehicles]);

  // 総重量・総体積計算（配送先）
  const totalDelivery = useMemo(() => {
    const weight = selectedDeliveries.reduce((sum, d) => sum + d.weight, 0);
    const volume = selectedDeliveries.reduce((sum, d) => sum + d.volume, 0);
    return { weight, volume };
  }, [selectedDeliveries]);

  // 車両テーブルのカラム定義
  const vehicleColumns: ColumnsType<Vehicle> = [
    {
      title: '車両ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
    },
    {
      title: 'タイプ',
      dataIndex: 'vehicle_type',
      key: 'type',
      width: 80,
    },
    {
      title: '容量(重量)',
      dataIndex: 'capacity_weight',
      key: 'weight',
      width: 100,
      render: (weight: number) => `${weight.toLocaleString()} kg`,
    },
    {
      title: '容量(体積)',
      dataIndex: 'capacity_volume',
      key: 'volume',
      width: 100,
      render: (volume: number) => `${volume.toFixed(1)} m³`,
    },
    {
      title: 'コスト(km)',
      dataIndex: 'cost_per_km',
      key: 'cost_km',
      width: 100,
      render: (cost: number) => `¥${cost.toLocaleString()}/km`,
    },
    {
      title: 'コスト(時)',
      dataIndex: 'cost_per_hour',
      key: 'cost_hour',
      width: 100,
      render: (cost: number) => `¥${cost.toLocaleString()}/h`,
    },
  ];

  // 配送先テーブルのカラム定義
  const deliveryColumns: ColumnsType<Delivery> = [
    {
      title: '配送先ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      fixed: 'left',
    },
    {
      title: '顧客名',
      dataIndex: 'customer_name',
      key: 'name',
      width: 120,
    },
    {
      title: '時間窓',
      dataIndex: 'time_window',
      key: 'time_window',
      width: 100,
      render: (timeWindow: string | null) => {
        if (timeWindow === 'morning') {
          return <Tag color="red">午前指定</Tag>;
        } else if (timeWindow === 'afternoon') {
          return <Tag color="gold">午後指定</Tag>;
        } else {
          return <Tag color="green">指定なし</Tag>;
        }
      },
    },
    {
      title: '重量',
      dataIndex: 'weight',
      key: 'weight',
      width: 100,
      render: (weight: number) => `${weight.toLocaleString()} kg`,
    },
    {
      title: '体積',
      dataIndex: 'volume',
      key: 'volume',
      width: 80,
      render: (volume: number) => `${volume.toFixed(1)} m³`,
    },
    {
      title: 'サービス時間',
      dataIndex: 'service_time',
      key: 'service_time',
      width: 100,
      render: (time: number) => `${time}分`,
    },
  ];

  // 拠点が選択されていない場合
  if (selectedDepots.length === 0) {
    return (
      <Drawer
        title="選択状態詳細"
        placement="right"
        width={720}
        open={visible}
        onClose={onClose}
      >
        <Text type="secondary">拠点が選択されていません</Text>
      </Drawer>
    );
  }

  const depot = selectedDepots[0]; // 単一拠点を前提

  return (
    <Drawer
      title="選択状態詳細"
      placement="right"
      width={720}
      open={visible}
      onClose={onClose}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* セクション 1: 拠点詳細 */}
        <div>
          <Title level={5}>拠点情報（{selectedDepots.length}件選択中）</Title>
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label="ID">{depot.id}</Descriptions.Item>
            <Descriptions.Item label="名称">{depot.name}</Descriptions.Item>
            <Descriptions.Item label="住所">{depot.address}</Descriptions.Item>
            <Descriptions.Item label="座標">
              ({depot.latitude.toFixed(4)}, {depot.longitude.toFixed(4)})
            </Descriptions.Item>
            <Descriptions.Item label="営業時間">
              {depot.operating_hours.start_time} - {depot.operating_hours.end_time}
            </Descriptions.Item>
          </Descriptions>
        </div>

        {/* セクション 2: 車両詳細（テーブル形式） */}
        <div>
          <Title level={5}>車両一覧（{selectedVehicles.length}台選択中）</Title>
          <Table
            dataSource={selectedVehicles}
            columns={vehicleColumns}
            rowKey="id"
            pagination={false}
            size="small"
            scroll={{ x: 'max-content' }}
            footer={() => (
              <Text strong>
                総容量: {totalCapacity.weight.toLocaleString()} kg, {totalCapacity.volume.toFixed(1)} m³
              </Text>
            )}
          />
        </div>

        {/* セクション 3: 配送先詳細（テーブル形式、ページネーション） */}
        <div>
          <Title level={5}>配送先一覧（{selectedDeliveries.length}件選択中）</Title>
          <Table
            dataSource={sortedDeliveries}
            columns={deliveryColumns}
            rowKey="id"
            pagination={{ pageSize: 10, showSizeChanger: false }}
            size="small"
            scroll={{ x: 'max-content' }}
            footer={() => (
              <Text strong>
                総重量: {totalDelivery.weight.toLocaleString()} kg, 総体積:{' '}
                {totalDelivery.volume.toFixed(1)} m³
              </Text>
            )}
          />
        </div>
      </Space>
    </Drawer>
  );
};
