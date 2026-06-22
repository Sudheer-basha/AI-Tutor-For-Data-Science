import React, { useState, useEffect, useContext } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, BookOpen, HelpCircle, FileEdit, AlertTriangle } from 'lucide-react'
import { AuthContext, API_URL } from '../App'
import AIChat from '../components/AIChat'
import { marked } from 'marked'

function Course() {
  const { lesson_id } = useParams()
  const { token } = useContext(AuthContext)
  const [lesson, setLesson] = useState(null)
  const [assignment, setAssignment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const fetchLessonAndAssignment = async () => {
      setLoading(true)
      setError('')
      try {
        // 1. Fetch lesson details
        const lessonRes = await fetch(`${API_URL}/api/lessons/${lesson_id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!lessonRes.ok) {
          if (lessonRes.status === 403) {
            setError('LOCKED')
          } else {
            setError('Failed to load lesson.')
          }
          setLoading(false)
          return
        }

        const lessonData = await lessonRes.json()
        setLesson(lessonData)

        // 2. Fetch corresponding assignment details
        const assignRes = await fetch(`${API_URL}/api/assignments/by-lesson/${lesson_id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (assignRes.ok) {
          const assignData = await assignRes.json()
          setAssignment(assignData)
        }
      } catch (err) {
        console.error("Error loading course details:", err)
        setError('A network error occurred.')
      } finally {
        setLoading(false)
      }
    }

    fetchLessonAndAssignment()
  }, [lesson_id, token])

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

  // Handle Locked Lesson Error Screen
  if (error === 'LOCKED') {
    return (
      <div style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <div className="glass-panel" style={{ padding: '3rem', borderLeft: '4px solid var(--danger)' }}>
          <AlertTriangle size={48} color="var(--danger)" style={{ marginBottom: '1.5rem' }} />
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Lesson Locked</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
            This lesson is locked. To access it, you must complete and pass the quiz and coding assignment for all previous lessons.
          </p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            <ArrowLeft size={16} />
            <span>Go Back to Dashboard</span>
          </button>
        </div>
      </div>
    )
  }

  if (error || !lesson) {
    return (
      <div style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <div className="glass-panel" style={{ padding: '3rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Error</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{error || 'Lesson not found.'}</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            <span>Go to Dashboard</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="course-page-container">
      {/* Left Column: Lesson Content */}
      <div className="lesson-viewer">
        {/* Navigation Bar */}
        <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
          <button 
            onClick={() => navigate('/')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.9rem',
              padding: '0.5rem 0'
            }}
          >
            <ArrowLeft size={16} />
            <span>Roadmap Dashboard</span>
          </button>
        </div>

        {/* Lesson Body Card */}
        <div className="glass-panel lesson-content-card">
          <div style={{ marginBottom: '2rem' }}>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--primary)', fontWeight: 700 }}>
              Week {lesson.week_number} • Month {lesson.month_number}
            </span>
            <h1 style={{ fontSize: '2.2rem', marginTop: '0.25rem', marginBottom: '0.5rem' }}>{lesson.title}</h1>
          </div>
          
          <div 
            className="markdown-body"
            dangerouslySetInnerHTML={{ __html: marked.parse(lesson.content || '') }}
          />
        </div>

        {/* Action Panel in Footer */}
        <div className="glass-panel lesson-footer-nav" style={{ padding: '1.5rem 2rem' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
            Finished reading? Prove your mastery:
          </span>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate(`/quiz/${lesson.lesson_id}`)}
            >
              <HelpCircle size={18} color="var(--primary)" />
              <span>Take Lesson Quiz</span>
            </button>
            {assignment && (
              <button 
                className="btn btn-primary"
                onClick={() => navigate(`/assignments/${assignment.assignment_id}`)}
              >
                <FileEdit size={18} />
                <span>Submit Assignment</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Right Column: AI Tutor Chat */}
      <div className="ai-tutor-sidebar">
        <AIChat lessonId={lesson.lesson_id} />
      </div>
    </div>
  )
}

export default Course
