/**
 * AI自動配車システム - 結果パネルコンポーネント（完全版）
 *
 * 最適化結果の詳細表示
 * - 改善指標カード
 * - ルート一覧テーブル
 * - コスト比較チャート
 */

import React, { useState } from 'react';
import { Card, Tabs, Row, Col, Statistic, Table, Space, Tag, Typography } from 'antd';
import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  DollarOutlined,
  RiseOutlined,
  ClockCircleOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useVRPStore } from '../../stores/useVRPStore';
import type { Route } from '../../types';
import { ComparisonTab } from './ComparisonTab';

const { Title, Text } = Typography;

/**
 * 改善指標カードセクション
 */
const ImprovementCards: React.FC = () => {
  const { optimizationResult } = useVRPStore();
  if (!optimizationResult) return null;

  const { improvement_metrics, computation_time } = optimizationResult;

  return (
    <Row gutter={16}>
      <Col span={6}>
        <Card>
          <Statistic
            title="距離削減"
            value={improvement_metrics.distance_reduction_percent.toFixed(1)}
            precision={1}
            suffix="%"
            prefix={
              improvement_metrics.distance_reduction_percent > 0 ? (
                <ArrowDownOutlined style={{ color: '#52c41a' }} />
              ) : (
                <ArrowUpOutlined style={{ color: '#ff4d4f' }} />
              )
            }
            valueStyle={{
              color:
                improvement_metrics.distance_reduction_percent > 0 ? '#52c41a' : '#ff4d4f',
            }}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {improvement_metrics.distance_reduction_km.toFixed(1)} km 削減
          </Text>
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="コスト削減"
            value={improvement_metrics.cost_reduction_percent.toFixed(1)}
            precision={1}
            suffix="%"
            prefix={<DollarOutlined />}
            valueStyle={{
              color:
                improvement_metrics.cost_reduction_percent > 0 ? '#52c41a' : '#ff4d4f',
            }}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            ¥{improvement_metrics.cost_reduction_amount.toLocaleString()} 削減
          </Text>
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="積載率改善"
            value={improvement_metrics.utilization_improvement_percent.toFixed(1)}
            precision={1}
            suffix="%"
            prefix={<RiseOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            効率的な荷物配分
          </Text>
        </Card>
      </Col>
      <Col span={6}>
        <Card>
          <Statistic
            title="計算時間"
            value={(computation_time / 1000).toFixed(1)}
            precision={1}
            suffix="秒"
            prefix={<ClockCircleOutlined />}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            OR-Tools CVRPTW
          </Text>
        </Card>
      </Col>
    </Row>
  );
};

/**
 * ルート一覧テーブル
 */
const RouteTable: React.FC = () => {
  const { optimizationResult, setActiveRouteId } = useVRPStore();
  if (!optimizationResult) return null;

  const { routes } = optimizationResult;

  const columns = [
    {
      title: 'ルート',
      dataIndex: 'index',
      key: 'index',
      width: 80,
      render: (_: any, __: any, index: number) => (
        <Tag color="blue">ルート {index + 1}</Tag>
      ),
    },
    {
      title: '車両ID',
      dataIndex: 'vehicle_id',
      key: 'vehicle_id',
      width: 120,
    },
    {
      title: '停車数',
      dataIndex: 'stops',
      key: 'stops',
      width: 80,
      render: (stops: any[]) => `${stops.length} 箇所`,
    },
    {
      title: '総距離',
      dataIndex: 'total_distance',
      key: 'total_distance',
      width: 100,
      render: (distance: number) => `${distance.toFixed(1)} km`,
    },
    {
      title: '総時間',
      dataIndex: 'total_duration',
      key: 'total_duration',
      width: 100,
      render: (duration: number) => `${duration} 分`,
    },
    {
      title: '総コスト',
      dataIndex: 'total_cost',
      key: 'total_cost',
      width: 120,
      render: (cost: number) => `¥${cost.toLocaleString()}`,
    },
    {
      title: '積載率（重量）',
      dataIndex: 'utilization_weight',
      key: 'utilization_weight',
      width: 120,
      render: (utilization: number) => (
        <Tag color={utilization > 70 ? 'green' : utilization > 50 ? 'orange' : 'red'}>
          {utilization.toFixed(1)}%
        </Tag>
      ),
    },
    {
      title: '積載率（体積）',
      dataIndex: 'utilization_volume',
      key: 'utilization_volume',
      width: 120,
      render: (utilization: number) => (
        <Tag color={utilization > 70 ? 'green' : utilization > 50 ? 'orange' : 'red'}>
          {utilization.toFixed(1)}%
        </Tag>
      ),
    },
  ];

  return (
    <Table
      dataSource={routes}
      columns={columns}
      rowKey="id"
      pagination={false}
      scroll={{ x: 800 }}
      size="small"
      onRow={(record) => ({
        onClick: () => setActiveRouteId(record.id),
        style: { cursor: 'pointer' },
      })}
    />
  );
};

/**
 * コスト比較チャート
 */
const CostChart: React.FC = () => {
  const { optimizationResult } = useVRPStore();
  if (!optimizationResult) return null;

  const { baseline_metrics, total_cost, total_distance, total_duration } = optimizationResult;

  const chartData = [
    {
      name: '基線\n(simple_assignment)',
      距離: baseline_metrics.total_distance.toFixed(1),
      コスト: baseline_metrics.total_cost,
      時間: baseline_metrics.total_duration,
    },
    {
      name: '最適化後\n(OR-Tools)',
      距離: total_distance.toFixed(1),
      コスト: total_cost,
      時間: total_duration,
    },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <div>
        <Title level={5}>距離比較 (km)</Title>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="距離" fill="#1890ff" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <Title level={5}>コスト比較 (¥)</Title>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="コスト" fill="#52c41a" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Space>
  );
};

/**
 * 結果パネルメインコンポーネント
 */
export const ResultPanel: React.FC = () => {
  const { optimizationResult } = useVRPStore();
  const [activeTab, setActiveTab] = useState('overview');

  if (!optimizationResult) {
    return null;
  }

  const tabItems = [
    {
      key: 'overview',
      label: '📊 概要',
      children: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <ImprovementCards />
        </Space>
      ),
    },
    {
      key: 'routes',
      label: '🚛 ルート一覧',
      children: <RouteTable />,
    },
    {
      key: 'cost-chart',
      label: '📈 コスト比較',
      children: <CostChart />,
    },
    {
      key: 'comparison',
      label: (
        <span>
          <SwapOutlined /> 方案対比
        </span>
      ),
      children: <ComparisonTab />,
    },
  ];

  return (
    <div style={{ padding: '0 16px 16px' }}>
      <Card
        title={
          <Space>
            <Text strong>最適化結果</Text>
            <Tag color="green">成功</Tag>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {optimizationResult.routes.length} ルート生成
            </Text>
          </Space>
        }
        style={{ marginTop: 16 }}
      >
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={tabItems} />
      </Card>
    </div>
  );
};
