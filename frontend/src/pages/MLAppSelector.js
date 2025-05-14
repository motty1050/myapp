import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMLApp } from '../context/MLAppContext'
import MLAppCard from '../components/MLAppCard'
import { fetchMLApps } from '../services/api'

export default function MLAppSelector() {
  const [apps, setApps] = useState([])
  const { setSelectedApp } = useMLApp()
  const nav = useNavigate()

  useEffect(() => {
    fetchMLApps().then(setApps)
  }, [])

  const handleSelect = (app) => {
    setSelectedApp(app)
    nav(`/ml/${app.id}`)
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {apps.map(app => (
        <MLAppCard key={app.id} app={app} onClick={() => handleSelect(app)} />
      ))}
    </div>
  )
}
