import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// 利用可能な ML アプリ一覧を取得
export async function fetchMLApps() {
  const resp = await client.get('/ml-apps/')
  return resp.data  // [{id, name, description}, ...]
}

// 選択した ML アプリで予測実行
export async function fetchMLAppResult(appId, payload) {
  const resp = await client.post(`/ml/${appId}/predict/`, payload)
  return resp.data
}
