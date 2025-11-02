import { ConfigProvider } from 'antd'
import jaJP from 'antd/locale/ja_JP'

function App() {
  return (
    <ConfigProvider locale={jaJP}>
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h1>🚛 AI自動配車システム</h1>
        <p>デモプロトタイプ - フロントエンド起動成功！</p>
        <p>バージョン: 1.0.0</p>
        <p style={{ marginTop: '20px', color: '#666' }}>
          開発中...
        </p>
      </div>
    </ConfigProvider>
  )
}

export default App
