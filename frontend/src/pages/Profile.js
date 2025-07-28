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

  useEffect(() => {
    // 実際の実装では、ここでユーザー情報と統計データをAPIから取得
    // ダミーデータを設定
    setStats({
      totalPredictions: 42,
      favoriteApp: '画像分類モデル',
      lastUsed: '2024-01-15'
    })
  }, [])

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-6">プロフィール</h1>
      
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
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">メールアドレス</label>
              <input 
                type="email" 
                value={user.email} 
                onChange={(e) => setUser({...user, email: e.target.value})}
                className="mt-1 block w-full border border-gray-300 rounded-md p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">登録日</label>
              <p className="mt-1 text-gray-600">{user.joinDate}</p>
            </div>
          </div>
          <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors">
            保存
          </button>
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
              <tr>
                <td className="px-4 py-2 border-t">2024-01-15 14:30</td>
                <td className="px-4 py-2 border-t">画像分類モデル</td>
                <td className="px-4 py-2 border-t">0.25秒</td>
                <td className="px-4 py-2 border-t">猫 (95%)</td>
              </tr>
              <tr>
                <td className="px-4 py-2 border-t">2024-01-15 13:45</td>
                <td className="px-4 py-2 border-t">テキスト感情分析</td>
                <td className="px-4 py-2 border-t">0.12秒</td>
                <td className="px-4 py-2 border-t">ポジティブ (87%)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}