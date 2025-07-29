import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchMLAppResult } from '../services/api'
import { useMLApp } from '../context/MLAppContext'

export default function MLApp() {
  const { appId } = useParams()
  const { selectedApp } = useMLApp()
  const [result, setResult] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      setError(null)
    } else {
      setError('画像ファイルを選択してください')
    }
  }

  const handlePredict = async () => {
    if (!selectedFile) {
      setError('画像ファイルを選択してください')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const result = await fetchMLAppResult(appId, selectedFile)
      setResult(result)
    } catch (err) {
      setError(`予測に失敗しました: ${err.message}`)
      console.error('Prediction error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!selectedApp) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-lg">アプリ情報をロード中...</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-3xl font-bold mb-4">{selectedApp.name}</h2>
      <p className="text-gray-600 mb-6">{selectedApp.description}</p>
      
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">画像アップロード</h3>
        
        <div className="mb-4">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        {selectedFile && (
          <div className="mb-4">
            <p className="text-sm text-gray-600">選択されたファイル: {selectedFile.name}</p>
            <img
              src={URL.createObjectURL(selectedFile)}
              alt="Preview"
              className="mt-2 max-w-xs h-auto rounded border"
            />
          </div>
        )}

        <button
          onClick={handlePredict}
          disabled={!selectedFile || loading}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg font-medium"
        >
          {loading ? '予測中...' : '予測実行'}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-6">
            <h4 className="text-lg font-semibold mb-3">予測結果</h4>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <span className="font-medium">予測クラス:</span>
                  <span className="ml-2 text-lg font-bold text-blue-600">
                    {result.predicted_class}
                  </span>
                </div>
                <div>
                  <span className="font-medium">信頼度:</span>
                  <span className="ml-2 text-lg font-bold text-green-600">
                    {(result.confidence * 100).toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="font-medium">処理時間:</span>
                  <span className="ml-2">{(result.processing_time * 1000).toFixed(1)}ms</span>
                </div>
                <div>
                  <span className="font-medium">使用デバイス:</span>
                  <span className="ml-2">{result.device}</span>
                </div>
              </div>
              
              <div className="mt-4">
                <span className="font-medium">クラス別確率:</span>
                <div className="mt-2 space-y-2">
                  {Object.entries(result.class_probabilities || {}).map(([className, probability]) => (
                    <div key={className} className="flex justify-between items-center">
                      <span>{className}</span>
                      <span className="font-mono">{(probability * 100).toFixed(2)}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
