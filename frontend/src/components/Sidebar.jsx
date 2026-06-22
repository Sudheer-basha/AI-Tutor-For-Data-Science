import React, { useContext } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, BookOpen, User, LogOut, Flame, GraduationCap } from 'lucide-react'
import { AuthContext } from '../App'

function Sidebar() {
  const { user, logoutUser } = useContext(AuthContext)
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'My Profile', path: '/profile', icon: User },
  ]

  const handleLogout = () => {
    logoutUser()
    navigate('/login')
  }

  // Get initials for avatar placeholder
  const getInitials = (name) => {
    if (!name) return 'DS'
    return name
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase()
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <GraduationCap size={28} color="#6366f1" />
        <span className="sidebar-logo-text">AI DS Tutor</span>
      </div>

      <ul className="sidebar-menu">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <li 
              key={item.name} 
              className={`sidebar-item ${isActive ? 'active' : ''}`}
            >
              <Link to={item.path}>
                <Icon size={20} />
                <span>{item.name}</span>
              </Link>
            </li>
          )
        })}
      </ul>

      <div className="sidebar-footer">
        {user && (
          <div className="user-badge-sidebar">
            <div className="user-avatar">
              {getInitials(user.name)}
            </div>
            <div className="user-info-text">
              <span className="user-name">{user.name}</span>
              <span className="user-streak">
                <Flame size={14} fill="#f59e0b" color="#f59e0b" />
                <span>{user.streak_count} Day Streak</span>
              </span>
            </div>
          </div>
        )}

        <li className="sidebar-item" style={{ listStyle: 'none' }}>
          <a 
            href="#logout" 
            onClick={(e) => {
              e.preventDefault()
              handleLogout()
            }}
            style={{ color: '#ef4444' }}
          >
            <LogOut size={20} />
            <span>Logout</span>
          </a>
        </li>
      </div>
    </aside>
  )
}

export default Sidebar
