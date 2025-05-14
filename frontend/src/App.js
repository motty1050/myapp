import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Home from './pages/Home'
import Profile from './pages/Profile'
import MLAppSelector from './pages/MLAppSelector'
import MLApp from './pages/MLApp'
import { MLAppProvider } from './context/MLAppContext'

function App() {
  return (
    <BrowserRouter>
      <MLAppProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/ml-select" element={<MLAppSelector />} />
            {/* MLアプリ個別画面: appId を URL パラメータで受け取る */}
            <Route path="/ml/:appId" element={<MLApp />} />
          </Routes>
        </Layout>
      </MLAppProvider>
    </BrowserRouter>
  )
}

export default App
