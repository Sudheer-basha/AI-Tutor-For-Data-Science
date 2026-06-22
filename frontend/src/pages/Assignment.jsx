import React, { useState, useEffect, useContext } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, Award, CheckCircle, XCircle, Sparkles } from 'lucide-react'
import { AuthContext, API_URL } from '../App'
import { marked } from 'marked'

function Assignment() {
  const { assignment_id } = useParams()
  const { token } = useContext(AuthContext)
  const [assignment, setAssignment] = useState(null)
  const [submissionCode, setSubmissionCode] = useState('')
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  
  const navigate = useNavigate()

  useEffect(() => {
    const fetchAssignmentAndHistory = async () => {
      setLoading(true)
      setError('')
      try {
        // 1. Fetch assignment details
        const assignRes = await fetch(`${API_URL}/api/assignments/${assignment_id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (!assignRes.ok) {
          setError('Failed to load assignment.')
          setLoading(false)
          return
        }
        
        const assignData = await assignRes.json()
        setAssignment(assignData)

        // 2. Fetch student's prior submission if any
        const subRes = await fetch(`${API_URL}/api/assignments/submission/${assignment_id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (subRes.ok) {
          const subData = await subRes.json()
          setSubmissionCode(subData.submission_content)
          setEvaluation({
            score: subData.score,
            feedback: subData.feedback,
            status: subData.status
          })
        }
      } catch (err) {
        console.error("Error loading assignment details:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchAssignmentAndHistory()
  }, [assignment_id, token])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!submissionCode.trim() || submitting) return

    setSubmitting(true)
    setError('')
    
    try {
      const response = await fetch(`${API_URL}/api/assignments/${assignment_id}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ submission_content: submissionCode })
      })

      const data = await response.json()

      if (response.ok) {
        setEvaluation({
          score: data.score,
          feedback: data.feedback,
          status: data.status
        })

        // Alerts for badges or unlocking next week
        if (data.badge_earned) {
          alert(`🎉 Congratulations! You earned the "${data.badge_earned}" Badge! Check it out on your profile page.`)
        } else if (data.unlocked_next) {
          alert("🎉 Excellent work! The next lesson has been unlocked on your dashboard!")
        }
      } else {
        setError(data.detail || 'Failed to submit assignment.')
      }
    } catch (err) {
      console.error("Submission error:", err)
      setError('A connection error occurred. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

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

  if (error && !assignment) {
    return (
      <div style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <div className="glass-panel" style={{ padding: '3rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Error</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{error}</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            <span>Go to Dashboard</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      {/* Back to Lesson Link */}
      <div style={{ marginBottom: '1.5rem' }}>
        <button 
          onClick={() => navigate(`/lessons/${assignment.lesson_id}`)}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '0.9rem'
          }}
        >
          <ArrowLeft size={16} />
          <span>Back to Lesson Reading</span>
        </button>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--primary)', fontWeight: 700 }}>
          Practical Coding Assessment
        </span>
        <h1 style={{ fontSize: '2rem', marginTop: '0.25rem' }}>{assignment.title}</h1>
      </div>

      <div className="assignment-container">
        {/* Left Side: Description / Instructions */}
        <div className="glass-panel" style={{ padding: '2rem', alignSelf: 'start' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="var(--primary)" />
            <span>Instructions</span>
          </h2>
          <div 
            className="markdown-body"
            dangerouslySetInnerHTML={{ __html: marked.parse(assignment.description || '') }}
          />
        </div>

        {/* Right Side: Code Editor Workspace */}
        <div className="assignment-submit-panel">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                Write your script here:
              </span>
            </div>
            
            <textarea
              className="code-editor-area"
              value={submissionCode}
              onChange={(e) => setSubmissionCode(e.target.value)}
              placeholder="# Enter your Python code here..."
              required
            />

            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={!submissionCode.trim() || submitting}
              style={{ width: '100%' }}
            >
              {submitting ? (
                <>
                  <div className="typing-indicator" style={{ display: 'inline-flex', verticalAlign: 'middle', marginRight: '0.5rem' }}>
                    <div className="typing-dot" style={{ background: 'white' }}></div>
                    <div className="typing-dot" style={{ background: 'white' }}></div>
                    <div className="typing-dot" style={{ background: 'white' }}></div>
                  </div>
                  <span>AI Tutor is Evaluating...</span>
                </>
              ) : (
                <>
                  <Play size={16} fill="white" />
                  <span>Submit Code for AI Grading</span>
                </>
              )}
            </button>
          </form>

          {/* AI Evaluation Grade & Feedback Card */}
          {evaluation && (
            <div className={`glass-panel feedback-card ${evaluation.status === 'passed' ? 'passed' : 'failed'}`}>
              <div className="feedback-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {evaluation.status === 'passed' ? (
                    <CheckCircle size={24} color="var(--secondary)" />
                  ) : (
                    <XCircle size={24} color="var(--danger)" />
                  )}
                  <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>
                    {evaluation.status === 'passed' ? 'GRADED: PASSED' : 'GRADED: TRY AGAIN'}
                  </span>
                </div>
                <div className="score-badge">
                  {evaluation.score}/100
                </div>
              </div>
              <div 
                className="markdown-body"
                dangerouslySetInnerHTML={{ __html: marked.parse(evaluation.feedback || '') }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Assignment
