/**
 * AI自動配車システム - 方案対比Tabコンポーネント
 *
 * 基線方案（simple_assignment）と最適化後方案の詳細比較
 * Story 4.2: 最適化前後方案対比表示
 */

import React, { useMemo } from 'react';
import { Card, Row, Col, Statistic, Table, Alert, Tag } from 'antd';
import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  MinusOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useVRPStore } from '../../stores/useVRPStore';

/**
 * 安全除法：防止除零錯誤
 * @param numerator 分子
 * @param denominator 分母
 * @param defaultValue 分母為 0 時的默認值
 * @returns 計算結果或默認值
 */
const safeDivide = (
  numerator: number,
  denominator: number,
  defaultValue: number = 0
): number => {
  if (denominator === 0 || !isFinite(denominator)) {
    return defaultValue;
  }
  return numerator / denominator;
};

/**
 * 方案対比Tabコンポーネント
 *
 * 基線方案と最適化後方案の並列比較を表示します。
 * - 4つの総合比較指標カード（距離、コスト、積載率、車両数）
 * - ルート別詳細比較テーブル
 * - 改善率表示：絶対値 + 百分比（例：+19.5 pt (+100%)）
 * - Backend の vehicle_count 字段を使用
 */
export const ComparisonTab: React.FC = () => {
  const { optimizationResult } = useVRPStore();

  // 基線データチェック
  if (!optimizationResult || !optimizationResult.baseline_metrics) {
    return (
      <Alert
        message="基線方案データが利用できません"
        description="最適化結果に基線方案の情報が含まれていません。"
        type="warning"
        showIcon
      />
    );
  }

  const { baseline_metrics, improvement_metrics, routes } = optimizationResult;

  // 使用車両数
  const baselineVehicleCount = baseline_metrics.vehicle_count; // ✅ Backend から取得
  const optimizedVehicleCount = routes.length;

  // 総合比較データ
  const summaryStats = useMemo(() => {
    return [
      {
        title: '総距離',
        baseline: baseline_metrics.total_distance,
        optimized: optimizationResult.total_distance,
        diff: improvement_metrics.distance_reduction_km,
        percent: improvement_metrics.distance_reduction_percent,
        unit: 'km',
        formatter: (value: number) => `${value.toFixed(2)} km`,
      },
      {
        title: '総コスト',
        baseline: baseline_metrics.total_cost,
        optimized: optimizationResult.total_cost,
        diff: improvement_metrics.cost_reduction_amount,
        percent: improvement_metrics.cost_reduction_percent,
        unit: '¥',
        formatter: (value: number) => `¥${value.toLocaleString()}`,
      },
      {
        title: '平均積載率',
        baseline: baseline_metrics.average_utilization_weight,
        optimized: optimizationResult.average_utilization_weight,
        diff: improvement_metrics.utilization_improvement_percent,
        percent: improvement_metrics.utilization_improvement_percent,
        unit: '%',
        formatter: (value: number) => `${value.toFixed(1)}%`,
      },
      {
        title: '使用車両数',
        baseline: baselineVehicleCount,
        optimized: optimizedVehicleCount,
        diff: optimizedVehicleCount - baselineVehicleCount,
        percent: safeDivide(
          (optimizedVehicleCount - baselineVehicleCount) * 100,
          baselineVehicleCount
        ),
        unit: '台',
        formatter: (value: number) => `${value}台`,
      },
    ];
  }, [
    baseline_metrics,
    optimizationResult,
    improvement_metrics,
    baselineVehicleCount,
    optimizedVehicleCount,
  ]);

  // ルート別詳細比較テーブルデータ
  const detailTableData = useMemo(() => {
    // 配送先総数
    const totalStops = routes.reduce((sum, route) => sum + route.stops.length, 0);

    return [
      {
        key: 'vehicle_count',
        metric: '使用車両数',
        baseline: `${baselineVehicleCount}台`,
        optimized: `${optimizedVehicleCount}台`,
        diff: optimizedVehicleCount - baselineVehicleCount,
        diffPercent: safeDivide(
          (optimizedVehicleCount - baselineVehicleCount) * 100,
          baselineVehicleCount
        ).toFixed(1),
        isImprovement: optimizedVehicleCount < baselineVehicleCount,
      },
      {
        key: 'total_stops',
        metric: '総停車数',
        baseline: `${totalStops}件`,
        optimized: `${totalStops}件`,
        diff: 0,
        diffPercent: '0.0',
        isImprovement: true, // 中立
      },
      {
        key: 'total_distance',
        metric: '総距離',
        baseline: `${baseline_metrics.total_distance.toFixed(2)} km`,
        optimized: `${optimizationResult.total_distance.toFixed(2)} km`,
        diff: improvement_metrics.distance_reduction_km,
        diffPercent: improvement_metrics.distance_reduction_percent.toFixed(1),
        isImprovement: improvement_metrics.distance_reduction_km > 0,
      },
      {
        key: 'total_duration',
        metric: '総所要時間',
        baseline: `${Math.floor(baseline_metrics.total_duration / 60)}時間${
          baseline_metrics.total_duration % 60
        }分`,
        optimized: `${Math.floor(optimizationResult.total_duration / 60)}時間${
          optimizationResult.total_duration % 60
        }分`,
        diff: improvement_metrics.duration_reduction_minutes,
        diffPercent: (
          (improvement_metrics.duration_reduction_minutes / baseline_metrics.total_duration) *
          100
        ).toFixed(1),
        isImprovement: improvement_metrics.duration_reduction_minutes > 0,
      },
      {
        key: 'total_cost',
        metric: '総コスト',
        baseline: `¥${baseline_metrics.total_cost.toLocaleString()}`,
        optimized: `¥${optimizationResult.total_cost.toLocaleString()}`,
        diff: improvement_metrics.cost_reduction_amount,
        diffPercent: improvement_metrics.cost_reduction_percent.toFixed(1),
        isImprovement: improvement_metrics.cost_reduction_amount > 0,
      },
      {
        key: 'avg_utilization',
        metric: '平均積載率（重量）',
        baseline: `${baseline_metrics.average_utilization_weight.toFixed(1)}%`,
        optimized: `${optimizationResult.average_utilization_weight.toFixed(1)}%`,
        diff: improvement_metrics.utilization_improvement_percent,
        diffPercent: (
          (improvement_metrics.utilization_improvement_percent /
            baseline_metrics.average_utilization_weight) *
          100
        ).toFixed(1),
        isImprovement: improvement_metrics.utilization_improvement_percent > 0,
      },
      // 只有當 totalStops > 0 時才顯示距離/停車数和コスト/停車数
      ...(totalStops > 0
        ? [
            {
              key: 'distance_per_stop',
              metric: '距離/停車数',
              baseline: `${(baseline_metrics.total_distance / totalStops).toFixed(2)} km/件`,
              optimized: `${(optimizationResult.total_distance / totalStops).toFixed(2)} km/件`,
              diff:
                optimizationResult.total_distance / totalStops -
                baseline_metrics.total_distance / totalStops,
              diffPercent: (
                ((optimizationResult.total_distance / totalStops -
                  baseline_metrics.total_distance / totalStops) /
                  (baseline_metrics.total_distance / totalStops)) *
                100
              ).toFixed(1),
              isImprovement:
                optimizationResult.total_distance / totalStops <
                baseline_metrics.total_distance / totalStops,
            },
            {
              key: 'cost_per_stop',
              metric: 'コスト/停車数',
              baseline: `¥${Math.round(
                baseline_metrics.total_cost / totalStops
              ).toLocaleString()}/件`,
              optimized: `¥${Math.round(
                optimizationResult.total_cost / totalStops
              ).toLocaleString()}/件`,
              diff:
                Math.round(optimizationResult.total_cost / totalStops) -
                Math.round(baseline_metrics.total_cost / totalStops),
              diffPercent: (
                ((optimizationResult.total_cost / totalStops -
                  baseline_metrics.total_cost / totalStops) /
                  (baseline_metrics.total_cost / totalStops)) *
                100
              ).toFixed(1),
              isImprovement:
                optimizationResult.total_cost / totalStops <
                baseline_metrics.total_cost / totalStops,
            },
          ]
        : []),
    ];
  }, [
    baseline_metrics,
    optimizationResult,
    improvement_metrics,
    routes,
    baselineVehicleCount,
    optimizedVehicleCount,
  ]);

  // テーブルカラム定義
  const columns: ColumnsType<(typeof detailTableData)[0]> = [
    {
      title: '比較項目',
      dataIndex: 'metric',
      key: 'metric',
      width: 180,
      fixed: 'left',
    },
    {
      title: '基線方案',
      dataIndex: 'baseline',
      key: 'baseline',
      width: 150,
    },
    {
      title: '最適化方案',
      dataIndex: 'optimized',
      key: 'optimized',
      width: 150,
    },
    {
      title: '差分',
      key: 'diff',
      width: 200,
      render: (_, record) => {
        const diffValue = record.diff;
        const diffPercent = record.diffPercent;

        // 差分が0の場合
        if (Math.abs(diffValue) < 0.01) {
          return (
            <Tag icon={<MinusOutlined />} color="default">
              変化なし
            </Tag>
          );
        }

        // ✅ 決定事項: 絶対値 + 百分比を同時表示
        // 積載率は percentage point (pt) で表示
        const isUtilization = record.key === 'avg_utilization';
        const diffText = isUtilization
          ? `+${diffValue.toFixed(1)} pt (+${diffPercent}%)`
          : diffValue > 0
          ? `+${Math.abs(diffValue).toFixed(1)} (+${Math.abs(parseFloat(diffPercent))}%)`
          : `${diffValue.toFixed(1)} (${diffPercent}%)`;

        return (
          <Tag
            icon={
              record.isImprovement ? (
                <ArrowDownOutlined />
              ) : (
                <ArrowUpOutlined />
              )
            }
            color={record.isImprovement ? 'success' : 'error'}
          >
            {diffText}
          </Tag>
        );
      },
    },
  ];

  return (
    <div style={{ padding: '16px 0' }}>
      {/* 基線方案説明 */}
      <Alert
        message="基線方案について"
        description={`基線方案は「${baseline_metrics.method}」アルゴリズムで生成されています。これは最も単純な割当方式で、最適化前の状態を示します。OR-Tools による最適化との差分が改善効果を表します。`}
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* 総合比較カード */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {summaryStats.map((stat, index) => {
          const isImprovement = stat.diff > 0;
          const isNeutral = Math.abs(stat.diff) < 0.01;

          return (
            <Col span={6} key={index}>
              <Card>
                <Statistic
                  title={stat.title}
                  value={Math.abs(stat.diff)}
                  precision={2}
                  valueStyle={{
                    color: isNeutral
                      ? '#8c8c8c'
                      : isImprovement
                      ? '#52c41a'
                      : '#ff4d4f',
                    fontSize: 24,
                  }}
                  prefix={
                    isNeutral ? (
                      <MinusOutlined />
                    ) : isImprovement ? (
                      <ArrowDownOutlined />
                    ) : (
                      <ArrowUpOutlined />
                    )
                  }
                  suffix={`${stat.unit} (${stat.percent.toFixed(1)}%)`}
                />
                <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
                  <div>基線: {stat.formatter(stat.baseline)}</div>
                  <div>最適: {stat.formatter(stat.optimized)}</div>
                </div>
              </Card>
            </Col>
          );
        })}
      </Row>

      {/* ルート別詳細比較テーブル */}
      <Card title="ルート別詳細比較" bordered={false}>
        <Table
          dataSource={detailTableData}
          columns={columns}
          pagination={false}
          size="middle"
          scroll={{ x: 'max-content' }}
        />
      </Card>
    </div>
  );
};
