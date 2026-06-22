import React, { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, CheckCircle, Lock, PlayCircle, Flame, Award, HelpCircle, FileCheck, Percent } from 'lucide-react'
import { AuthContext, API_URL } from '../App'

function Dashboard() {
  const { user, token } = useContext(AuthContext)
  const [stats, setStats] = useState(null)
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch progress statistics
        const statsRes = await fetch(`${API_URL}/api/progress/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const statsData = await statsRes.json()
        setStats(statsData)

        // Fetch lessons roadmap
        const lessonsRes = await fetch(`${API_URL}/api/lessons`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const lessonsData = await lessonsRes.json()
        setLessons(lessonsData)
      } catch (err) {
        console.error("Error loading dashboard data:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [token])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem' }}>
        <div className="typing-indicator">
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
          <div className="typing-dot"></div>
        </div>
      </div>
    )
  }

  // Find the active lesson (first lesson that is 'unlocked' or fallback to the last completed one)
  const activeLesson = lessons.find(l => l.status === 'unlocked') || [...lessons].reverse().find(l => l.status === 'completed') || lessons[0]

  // Calculate overall course progress percentage
  const totalLessons = lessons.length || 12
  const completedCount = stats?.lessons_completed || 0
  const progressPercent = Math.min(Math.round((completedCount / totalLessons) * 100), 100)

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      {/* Header bar */}
      <div className="header-bar">
        <div className="page-title-section">
          <h1 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Welcome back, {user?.name}!</h1>
          <p className="page-subtitle">Here is your progress on the Personalized 3-Month Data Science learning path.</p>
        </div>
      </div>

      {/* Stats Summary Grid */}
      <div className="dashboard-grid">
        <div className="glass-panel stat-card">
          <div className="stat-icon-wrapper">
            <BookOpen size={24} />
          </div>
          <div className="stat-details">
            <span className="stat-value">{stats?.lessons_completed} / {totalLessons}</span>
            <span className="stat-label">Weeks Completed</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-icon-wrapper">
            <FileCheck size={24} />
          </div>
          <div className="stat-details">
            <span className="stat-value">{stats?.assignments_completed}</span>
            <span className="stat-label">Assignments Evaluated</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-icon-wrapper">
            <Percent size={24} />
          </div>
          <div className="stat-details">
            <span className="stat-value">{stats?.avg_quiz_score}%</span>
            <span className="stat-label">Average Quiz Score</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-icon-wrapper">
            <Award size={24} />
          </div>
          <div className="stat-details">
            <span className="stat-value">{stats?.total_badges}</span>
            <span className="stat-label">Badges Unlocked</span>
          </div>
        </div>
      </div>

      {/* Progress & Current Lesson Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1.2fr', gap: '2rem', marginBottom: '3rem' }}>
        {/* Progress Bar Container */}
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Overall Course Progress</span>
            <span style={{ color: 'var(--primary)' }}>{progressPercent}%</span>
          </h2>
          <div className="quiz-progress-bar" style={{ height: '10px', marginBottom: '1rem' }}>
            <div className="quiz-progress-fill" style={{ width: `${progressPercent}%` }}></div>
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Complete the quiz and assignment for each week to unlock the next topic. Finish all 12 weeks to generate your course certificate!
          </p>
        </div>

        {/* Current Lesson Hero Card */}
        {activeLesson && (
          <div className="glass-panel" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', justifySpace: 'between' }}>
            <div>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--primary)', fontWeight: 700 }}>
                Current Target (Week {activeLesson.week_number})
              </span>
              <h3 style={{ fontSize: '1.2rem', marginTop: '0.5rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>
                {activeLesson.title}
              </h3>
            </div>
            <button 
              className="btn btn-primary" 
              style={{ marginTop: 'auto', width: '100%' }}
              onClick={() => navigate(`/lessons/${activeLesson.lesson_id}`)}
            >
              <PlayCircle size={18} />
              <span>Resume Studying</span>
            </button>
          </div>
        )}
      </div>

      {/* 12-Week Roadmap Section */}
      <div className="roadmap-section">
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1.5rem' }}>Course Syllabus Roadmap</h2>
        <div className="roadmap-timeline">
          {lessons.map((lesson) => {
            const isCompleted = lesson.status === 'completed'
            const isUnlocked = lesson.status === 'unlocked'
            const isLocked = lesson.status === 'locked'

            return (
              <div 
                key={lesson.lesson_id} 
                className={`timeline-node ${isCompleted ? 'completed' : ''} ${isUnlocked ? 'unlocked' : ''} ${isLocked ? 'locked' : ''}`}
              >
                {/* Node marker icon */}
                <div className="timeline-marker">
                  {isCompleted ? (
                    <CheckCircle size={16} color="white" />
                  ) : isUnlocked ? (
                    <PlayCircle size={16} color="var(--primary)" />
                  ) : (
                    <Lock size={12} color="var(--text-muted)" />
                  )}
                </div>

                {/* Lesson Detail Card */}
                <div 
                  className={`glass-panel timeline-card ${!isLocked ? 'clickable' : ''}`}
                  onClick={() => !isLocked && navigate(`/lessons/${lesson.lesson_id}`)}
                >
                  <div className="timeline-header">
                    <span className="timeline-week">Week {lesson.week_number} • Month {lesson.month_number}</span>
                    <span className={`badge-pill ${isCompleted ? 'badge-completed' : isUnlocked ? 'badge-unlocked' : 'badge-locked'}`}>
                      {lesson.status}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', color: isLocked ? 'var(--text-secondary)' : 'var(--text-primary)' }}>
                    {lesson.title}
                  </h3>
                  {!isLocked && (
                    <p style={{ fontSize: '0.85rem', color: 'var(--primary)', marginTop: '0.75rem', fontWeight: 500 }}>
                      {isCompleted ? 'Review study material →' : 'Start learning →'}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
