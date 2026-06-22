import React, { useState, useEffect, useRef, useContext } from 'react'
import { Send, Sparkles, MessageCircle } from 'lucide-react'
import { AuthContext, API_URL } from '../App'
import { marked } from 'marked'

function AIChat({ lessonId }) {
  const { token } = useContext(AuthContext)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [sending, setSending] = useState(false)
  
  const messagesEndRef = useRef(null)

  // Scroll to the bottom of the chat pane
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Load chat history for the current lesson
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!lessonId) return
      
      try {
        const response = await fetch(`${API_URL}/api/tutor/history?lesson_id=${lessonId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          const data = await response.json()
          setMessages(data)
        }
      } catch (err) {
        console.error("Error loading chat history:", err)
      }
    }

    fetchChatHistory()
  }, [lessonId, token])

  // Scroll on message updates
  useEffect(() => {
    scrollToBottom()
  }, [messages, sending])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || sending) return

    const userMessageText = inputValue
    setInputValue('')
    setSending(true)

    // Append user message locally for instant UI update
    const tempUserMsg = {
      chat_id: Math.random().toString(),
      question: userMessageText,
      answer: '',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMsg])

    try {
      const response = await fetch(`${API_URL}/api/tutor/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          lesson_id: lessonId,
          question: userMessageText
        })
      })

      if (response.ok) {
        const data = await response.json()
        // Update messages with the final saved message from DB
        setMessages(prev => {
          const filtered = prev.filter(m => m.chat_id !== tempUserMsg.chat_id)
          return [...filtered, data]
        })
      } else {
        throw new Error("Chat call failed")
      }
    } catch (err) {
      console.error("Chat error:", err)
      setMessages(prev => {
        const filtered = prev.filter(m => m.chat_id !== tempUserMsg.chat_id)
        return [
          ...filtered,
          {
            chat_id: Math.random().toString(),
            question: userMessageText,
            answer: "⚠️ **Failed to connect**. Please ensure the backend is running and a valid Gemini API key is configured.",
            timestamp: new Date().toISOString()
          }
        ]
      })
    } finally {
      setSending(false)
    }
  }

  // Handle Ctrl+Enter / Enter behavior in textarea
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend(e)
    }
  }

  return (
    <div className="glass-panel ai-tutor-chatbox">
      {/* Chat panel header */}
      <div className="chat-header">
        <Sparkles size={18} color="#6366f1" />
        <span className="chat-header-title">AI Tutor Assistant</span>
        <div className="chat-header-status"></div>
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages">
        {messages.length === 0 && !sending && (
          <div style={{
            textAlign: 'center',
            color: 'var(--text-muted)',
            marginTop: '2rem',
            padding: '1rem',
            fontSize: '0.875rem'
          }}>
            <MessageCircle size={36} style={{ margin: '0 auto 1rem', opacity: 0.4 }} />
            <p>Have questions about this lesson? Ask me anything below!</p>
          </div>
        )}

        {messages.map((msg) => (
          <React.Fragment key={msg.chat_id}>
            {/* Question Message */}
            <div className="chat-message user">
              {msg.question}
            </div>
            
            {/* Answer Message */}
            {msg.answer && (
              <div className="chat-message tutor">
                <div 
                  className="markdown-body" 
                  dangerouslySetInnerHTML={{ __html: marked.parse(msg.answer) }}
                />
              </div>
            )}
          </React.Fragment>
        ))}

        {sending && (
          <div className="chat-message tutor" style={{ minWidth: '80px' }}>
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat input box */}
      <form onSubmit={handleSend} className="chat-input-area">
        <textarea
          placeholder="Ask a doubt..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows="1"
        />
        <button type="submit" className="chat-send-btn" disabled={!inputValue.trim() || sending}>
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}

export default AIChat
