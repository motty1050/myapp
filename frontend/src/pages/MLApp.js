import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchMLAppResult } from '../services/api'
import { useMLApp } from '../context/MLAppContext'

export default function MLApp() {
  const { appId } = useParams()
  const { selectedApp } = useMLApp()
  const [result, setResult] = useState(null)

  useEffect(() => {
    // 直接 URL で来た場合は selectedApp が null なので API からもアプリ情報を取得してもよい
    fetchMLAppResult(appId, {/* パラメータ */})
      .then(setResult)
  }, [appId])

  if (!selectedApp) {
    return <p>アプリ情報をロード中...</p>
  }

  return (
    <div>
      <h2 className="text-2xl">{selectedApp.name}</h2>
      {/* ここに入力フォームや結果表示コンポーネントを置く */}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
