import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="p-4 bg-gray-100 flex gap-4">
      <NavLink to="/" end className={({ isActive }) => isActive ? 'font-bold' : ''}>
        Home
      </NavLink>
      <NavLink to="/profile" className={({ isActive }) => isActive ? 'font-bold' : ''}>
        Profile
      </NavLink>
      <NavLink to="/ml-select" className={({ isActive }) => isActive ? 'font-bold' : ''}>
        ML Apps
      </NavLink>
    </nav>
  )
}
