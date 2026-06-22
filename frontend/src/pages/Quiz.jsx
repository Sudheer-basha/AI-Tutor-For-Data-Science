import React, { useState, useEffect, useContext } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Check, X, RefreshCw, CheckCircle, XCircle } from 'lucide-react'
import { AuthContext, API_URL } from '../App'

function Quiz() {
  const { lesson_id } = useParams()
  const { token } = useContext(AuthContext)
  const [questions, setQuestions] = useState([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const navigate = useNavigate()

  useEffect(() => {
    const fetchQuizData = async () => {
      setLoading(true)
      setError('')
      try {
        // 1. Fetch questions
        const questionsRes = await fetch(`${API_URL}/api/quizzes/by-lesson/${lesson_id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (!questionsRes.ok) {
          setError('Failed to load quiz. Please make sure the lesson is unlocked.')
          setLoading(false)
          return
        }

        const questionsData = await questionsRes.json()
        setQuestions(questionsData)

        // 2. Fetch submission status to check if already passed
        const statusRes = await fetch(`${API_URL}/api/quizzes/status/${lesson_id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (statusRes.ok) {
          const statusData = await statusRes.json()
          if (statusData.completed) {
            // Already taken, we can show a summary or allow them to retake.
            // For now, let them retake, but we've logged it.
          }
        }
      } catch (err) {
        console.error("Error loading quiz data:", err)
        setError('Network error.')
      } finally {
        setLoading(false)
      }
    }

    fetchQuizData()
  }, [lesson_id, token])

  const handleSelectOption = (quizId, optionLetter) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [quizId]: optionLetter
    }))
  }

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(prev => prev + 1)
    }
  }

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx(prev => prev - 1)
    }
  }

  const handleSubmit = async () => {
    // Format payload
    const formattedAnswers = Object.entries(selectedAnswers).map(([quiz_id, option]) => ({
      quiz_id,
      selected_option: option
    }))

    if (formattedAnswers.length < questions.length) {
      alert("Please answer all questions before submitting.")
      return
    }

    setSubmitting(true)
    try {
      const response = await fetch(`${API_URL}/api/quizzes/by-lesson/${lesson_id}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ answers: formattedAnswers })
      })

      if (response.ok) {
        const data = await response.json()
        setResult(data)

        if (data.badge_earned) {
          alert(`🎉 Congratulations! You earned the "${data.badge_earned}" Badge! Check it out on your profile page.`)
        } else if (data.unlocked_next) {
          alert("🎉 Excellent work! The next lesson has been unlocked on your dashboard!")
        }
      } else {
        alert("Failed to submit answers.")
      }
    } catch (err) {
      console.error("Submit quiz error:", err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleRetake = () => {
    setResult(null)
    setSelectedAnswers({})
    setCurrentIdx(0)
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

  if (error || questions.length === 0) {
    return (
      <div style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <div className="glass-panel" style={{ padding: '3rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Quiz Unavailable</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>{error || 'No questions seeded for this lesson.'}</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            <span>Go to Dashboard</span>
          </button>
        </div>
      </div>
    )
  }

  // Render Result Page if submitted
  if (result) {
    return (
      <div className="quiz-container" style={{ animation: 'fadeIn 0.4s ease-out' }}>
        <div className="glass-panel quiz-results-card">
          <div className={`quiz-results-icon ${!result.passed ? 'failed' : ''}`}>
            {result.passed ? <Check size={40} /> : <X size={40} />}
          </div>
          
          <h1 className="quiz-results-score">{result.score}%</h1>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
            {result.passed ? 'Assessment Passed!' : 'Assessment Failed'}
          </h2>
          <p className="quiz-results-text">
            {result.passed 
              ? `Congratulations! You answered ${result.correct_count} out of ${result.total_count} questions correctly.`
              : `You got ${result.correct_count} out of ${result.total_count} correct. A passing grade of 70% is required to complete this week.`}
          </p>

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '3rem' }}>
            <button className="btn btn-secondary" onClick={handleRetake}>
              <RefreshCw size={16} />
              <span>Retake Quiz</span>
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/')}>
              <span>Return to Dashboard</span>
            </button>
          </div>

          {/* Review Answers Details */}
          <div style={{ textAlign: 'left', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '2rem' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem' }}>Question Review</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {questions.map((q, idx) => {
                const detail = result.details.find(d => d.quiz_id === q.quiz_id)
                const isCorrect = detail?.correct
                const userAns = detail?.user_option
                const correctAns = detail?.correct_option

                return (
                  <div key={q.quiz_id} style={{ 
                    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                    paddingBottom: '1.5rem'
                  }}>
                    <p style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'start', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{idx + 1}.</span>
                      <span>{q.question}</span>
                    </p>
                    <div style={{ paddingLeft: '1.25rem', fontSize: '0.9rem' }}>
                      <p style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: isCorrect ? 'var(--secondary)' : 'var(--danger)' }}>
                        {isCorrect ? <CheckCircle size={14} /> : <XCircle size={14} />}
                        <span>Your Answer: {userAns} ({q.options[userAns.charCodeAt(0) - 65]})</span>
                      </p>
                      {!isCorrect && (
                        <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem', paddingLeft: '1.25rem' }}>
                          Correct Answer: {correctAns} ({q.options[correctAns.charCodeAt(0) - 65]})
                        </p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Active question details
  const activeQuestion = questions[currentIdx]
  const progressPercent = ((currentIdx) / questions.length) * 100
  const optionLetters = ['A', 'B', 'C', 'D']

  return (
    <div className="quiz-container" style={{ animation: 'fadeIn 0.3s ease-out' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <button 
          onClick={() => navigate(`/lessons/${lesson_id}`)}
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
          Theoretical Check
        </span>
        <h1 style={{ fontSize: '1.75rem', marginTop: '0.25rem' }}>Lesson MCQ Quiz</h1>
      </div>

      {/* Quiz Progress */}
      <div className="quiz-progress-bar">
        <div className="quiz-progress-fill" style={{ width: `${progressPercent}%` }}></div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        <span>Question {currentIdx + 1} of {questions.length}</span>
        <span>{Math.round(progressPercent)}% Complete</span>
      </div>

      {/* Question Card */}
      <div className="glass-panel quiz-question-card">
        <p className="quiz-question-text">{activeQuestion.question}</p>
        
        <div className="quiz-options-list">
          {activeQuestion.options.map((option, idx) => {
            const letter = optionLetters[idx]
            const isSelected = selectedAnswers[activeQuestion.quiz_id] === letter
            
            return (
              <div 
                key={letter}
                className={`quiz-option ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSelectOption(activeQuestion.quiz_id, letter)}
              >
                <div className="quiz-option-letter">{letter}</div>
                <div style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{option}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Navigation Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button 
          className="btn btn-secondary" 
          onClick={handlePrev}
          disabled={currentIdx === 0}
        >
          Previous
        </button>

        {currentIdx === questions.length - 1 ? (
          <button 
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={submitting || Object.keys(selectedAnswers).length < questions.length}
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </button>
        ) : (
          <button 
            className="btn btn-primary" 
            onClick={handleNext}
            disabled={!selectedAnswers[activeQuestion.quiz_id]}
          >
            Next
          </button>
        )}
      </div>
    </div>
  )
}

export default Quiz
