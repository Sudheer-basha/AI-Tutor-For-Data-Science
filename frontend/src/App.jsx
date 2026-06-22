import React, { createContext, useState, useEffect, useContext } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Course from './pages/Course'
import Assignment from './pages/Assignment'
import Quiz from './pages/Quiz'
import Profile from './pages/Profile'

// Create Auth Context for sharing state across pages
export const AuthContext = createContext(null)

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Component to protect routes from unauthenticated users
const ProtectedLayout = ({ children }) => {
  const { user, loading } = useContext(AuthContext)
  const location = useLocation()

  if (loading) {
    return (
      <div style={{
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh', 
        fontFamily: 'Outfit, sans-serif',
        fontSize: '1.25rem',
        color: '#6366f1'
      }}>
        <div className="typing-indicator">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

function App() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [loading, setLoading] = useState(true)

  // Fetch current user details whenever the token changes
  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setUser(null)
        setLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        } else {
          // Token expired or invalid
          localStorage.removeItem('token')
          setToken('')
          setUser(null)
        }
      } catch (err) {
        console.error("Error fetching current user:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [token])

  const loginUser = (newToken) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
  }

  const logoutUser = () => {
    localStorage.removeItem('token')
    setToken('')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, loginUser, logoutUser, setUser }}>
      <Router>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/" replace />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/" replace />} />

          {/* Protected Application Routes */}
          <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
          <Route path="/lessons/:lesson_id" element={<ProtectedLayout><Course /></ProtectedLayout>} />
          <Route path="/assignments/:assignment_id" element={<ProtectedLayout><Assignment /></ProtectedLayout>} />
          <Route path="/quiz/:lesson_id" element={<ProtectedLayout><Quiz /></ProtectedLayout>} />
          <Route path="/profile" element={<ProtectedLayout><Profile /></ProtectedLayout>} />

          {/* Redirect any other request to Dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthContext.Provider>
  )
}

export default App
