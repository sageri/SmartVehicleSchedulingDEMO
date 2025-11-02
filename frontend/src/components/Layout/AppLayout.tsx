/**
 * AI自動配車システム - メインレイアウト
 *
 * Ant Design Layout による全体レイアウト
 * - Header: タイトル
 * - Sider: 操作パネル（左側）
 * - Content: 地図 + 結果表示（右側）
 */

import React from 'react';
import { Layout } from 'antd';
import { RocketOutlined } from '@ant-design/icons';

const { Header: AntHeader, Sider: AntSider, Content: AntContent } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
  sider: React.ReactNode;
}

/**
 * アプリケーション全体のレイアウトコンポーネント
 */
export const AppLayout: React.FC<AppLayoutProps> = ({ children, sider }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* ヘッダー */}
      <AntHeader
        style={{
          background: '#001529',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
        }}
      >
        <RocketOutlined style={{ fontSize: 24, marginRight: 12 }} />
        <h1 style={{ color: '#fff', margin: 0, fontSize: 20 }}>
          AI自動配車システム - Demo
        </h1>
      </AntHeader>

      <Layout>
        {/* サイドバー（操作パネル） */}
        <AntSider
          width={360}
          style={{
            background: '#fff',
            borderRight: '1px solid #f0f0f0',
            overflowY: 'auto',
            height: 'calc(100vh - 64px)',
          }}
        >
          <div style={{ padding: 16 }}>{sider}</div>
        </AntSider>

        {/* メインコンテンツ（地図 + 結果） */}
        <AntContent
          style={{
            background: '#f0f2f5',
            padding: 0,
            overflow: 'hidden',
          }}
        >
          {children}
        </AntContent>
      </Layout>
    </Layout>
  );
};
