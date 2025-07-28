export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-6">ML推論アプリへようこそ</h1>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-semibold mb-4 text-blue-800">
          このアプリについて
        </h2>
        <p className="text-gray-700 mb-4">
          このアプリケーションは、複数の機械学習モデルを簡単に試すことができるプラットフォームです。
        </p>
        <ul className="list-disc list-inside text-gray-700 space-y-2">
          <li>様々なMLモデルを選択して予測を実行</li>
          <li>リアルタイムでの推論結果の確認</li>
          <li>推論履歴の管理と分析</li>
        </ul>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-xl font-semibold mb-3">🚀 はじめる</h3>
          <p className="text-gray-600 mb-4">
            MLアプリセレクターから利用したいモデルを選択してください。
          </p>
          <a 
            href="/ml-select" 
            className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            MLアプリを選択
          </a>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-xl font-semibold mb-3">👤 プロフィール</h3>
          <p className="text-gray-600 mb-4">
            ユーザー設定や推論履歴を確認できます。
          </p>
          <a 
            href="/profile" 
            className="inline-block bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
          >
            プロフィールを表示
          </a>
        </div>
      </div>
    </div>
  )
}