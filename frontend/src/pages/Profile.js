import { useState, useEffect } from 'react'

export default function Profile() {
  const [user, setUser] = useState({
    name: 'ユーザー',
    email: 'user@example.com',
    joinDate: '2024-01-01'
  })
  
  const [stats, setStats] = useState({
    totalPredictions: 0,
    favoriteApp: 'なし',
    lastUsed: 'なし'
  })

  const [recentPredictions, setRecentPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saveStatus, setSaveStatus] = useState('')

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setLoading(true)
        // 実際のAPI呼び出しをシミュレート
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // ダミーデータを設定
        setStats({
          totalPredictions: 42,
          favoriteApp: '画像分類モデル',
          lastUsed: '2024-07-28'
        })

        setRecentPredictions([
          {
            id: 1,
            timestamp: '2024-07-28 14:30',
            appName: '画像分類モデル',
            processingTime: '0.25秒',
            result: '猫 (95%)'
          },
          {
            id: 2,
            timestamp: '2024-07-28 13:45',
            appName: 'テキスト感情分析',
            processingTime: '0.12秒',
            result: 'ポジティブ (87%)'
          },
          {
            id: 3,
            timestamp: '2024-07-27 16:20',
            appName: '画像分類モデル',
            processingTime: '0.31秒',
            result: '犬 (92%)'
          }
        ])
        
        setError('')
      } catch (err) {
        setError('データの取得に失敗しました。')
        console.error('Error fetching user data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchUserData()
  }, [])

  const handleSaveProfile = async () => {
    try {
      setSaveStatus('保存中...')
      // 実際のAPI呼び出しをシミュレート
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSaveStatus('保存しました！')
      setTimeout(() => setSaveStatus(''), 3000)
    } catch (err) {
      setSaveStatus('保存に失敗しました。')
      console.error('Error saving profile:', err)
      setTimeout(() => setSaveStatus(''), 3000)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-6">プロフィール</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          <div className="grid md:grid-cols-2 gap-6">
            {/* ユーザー情報 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <h2 className="text-2xl font-semibold mb-4">ユーザー情報</h2>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">名前</label>
                  <input 
                    type="text" 
                    value={user.name} 
                    onChange={(e) => setUser({...user, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">メールアドレス</label>
                  <input 
                    type="email" 
                    value={user.email} 
                    onChange={(e) => setUser({...user, email: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">登録日</label>
                  <p className="mt-1 text-gray-600">{user.joinDate}</p>
                </div>
              </div>
              <button 
                onClick={handleSaveProfile}
                disabled={saveStatus === '保存中...'}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saveStatus || '保存'}
              </button>
              {saveStatus && (
                <p className={`mt-2 text-sm ${saveStatus.includes('失敗') ? 'text-red-600' : 'text-green-600'}`}>
                  {saveStatus}
                </p>
              )}
            </div>

            {/* 使用統計 */}
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <h2 className="text-2xl font-semibold mb-4">使用統計</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-gray-700">総推論回数</span>
                  <span className="font-semibold text-blue-600">{stats.totalPredictions}</span>
                </div>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-gray-700">よく使うアプリ</span>
                  <span className="font-semibold">{stats.favoriteApp}</span>
                </div>
                <div className="flex justify-between items-center border-b pb-2">
                  <span className="text-gray-700">最終利用日</span>
                  <span className="font-semibold">{stats.lastUsed}</span>
                </div>
              </div>
            </div>
          </div>

          {/* 最近の推論履歴 */}
          <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <h2 className="text-2xl font-semibold mb-4">最近の推論履歴</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">日時</th>
                    <th className="px-4 py-2 text-left">アプリ</th>
                    <th className="px-4 py-2 text-left">処理時間</th>
                    <th className="px-4 py-2 text-left">結果</th>
                  </tr>
                </thead>
                <tbody>
                  {recentPredictions.map((prediction) => (
                    <tr key={prediction.id}>
                      <td className="px-4 py-2 border-t">{prediction.timestamp}</td>
                      <td className="px-4 py-2 border-t">{prediction.appName}</td>
                      <td className="px-4 py-2 border-t">{prediction.processingTime}</td>
                      <td className="px-4 py-2 border-t">{prediction.result}</td>
                    </tr>
                  ))}
                  {recentPredictions.length === 0 && (
                    <tr>
                      <td colSpan="4" className="px-4 py-8 text-center text-gray-500">
                        推論履歴がありません
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}