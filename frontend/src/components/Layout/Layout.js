import Navbar from './Navbar'

export default function Layout({ children }) {
  return (
    <div>
      <Navbar />
      <main className="p-6">
        {children}
      </main>
    </div>
  )
}
