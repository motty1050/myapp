import { createContext, useState, useContext } from 'react'

const MLAppContext = createContext()

export function MLAppProvider({ children }) {
  const [selectedApp, setSelectedApp] = useState(null)
  return (
    <MLAppContext.Provider value={{ selectedApp, setSelectedApp }}>
      {children}
    </MLAppContext.Provider>
  )
}

export const useMLApp = () => useContext(MLAppContext)
