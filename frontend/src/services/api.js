import axios from 'axios'

const client = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
})

// 利用可能な ML アプリ一覧を取得
export async function fetchMLApps() {
  const resp = await client.get('/ml-apps/')
  return resp.data  // [{id, name, description}, ...]
}

// 選択した ML アプリで予測実行
export async function fetchMLAppResult(appId, imageFile) {
  const formData = new FormData()
  formData.append('image', imageFile)
  
  const resp = await client.post(`/ml-apps/${appId}/predict/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return resp.data
}
