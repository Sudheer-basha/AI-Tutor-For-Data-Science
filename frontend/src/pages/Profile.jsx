import React, { useState, useEffect, useContext } from 'react'
import { Award, Flame, Download, Lock, CheckCircle, Trophy, RefreshCw } from 'lucide-react'
import { AuthContext, API_URL } from '../App'

function Profile() {
  const { user, token } = useContext(AuthContext)
  const [stats, setStats] = useState(null)
  const [badges, setBadges] = useState([])
  const [certificate, setCertificate] = useState(null)
  const [certEligible, setCertEligible] = useState(false)
  const [generatingCert, setGeneratingCert] = useState(false)
  const [loading, setLoading] = useState(true)

  const fetchProfileData = async () => {
    try {
      // 1. Fetch dashboard stats (to check completion count)
      const statsRes = await fetch(`${API_URL}/api/progress/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const statsData = await statsRes.json()
      setStats(statsData)
      
      // Determine if they completed all 12 weeks
      if (statsData.lessons_completed >= 12) {
        setCertEligible(true)
      }

      // 2. Fetch badges
      const badgesRes = await fetch(`${API_URL}/api/progress/badges`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const badgesData = await badgesRes.json()
      setBadges(badgesData)

      // 3. Fetch certificate details
      const certRes = await fetch(`${API_URL}/api/certificates`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (certRes.ok) {
        const certData = await certRes.json()
        setCertificate(certData)
      }
    } catch (err) {
      console.error("Error loading profile details:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfileData()
  }, [token])

  const handleGenerateCertificate = async () => {
    setGeneratingCert(true)
    try {
      const response = await fetch(`${API_URL}/api/certificates/generate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const certData = await response.json()
        setCertificate(certData)
        alert("🎉 Congratulations! Your official Certificate of Completion has been generated!")
      } else {
        const errData = await response.json()
        alert(errData.detail || "Failed to generate certificate.")
      }
    } catch (err) {
      console.error(err)
      alert("Error generating certificate.")
    } finally {
      setGeneratingCert(false)
    }
  }

  const handleDownloadCertificate = async () => {
    try {
      const response = await fetch(`${API_URL}/api/certificates/download`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (!response.ok) throw new Error("Download failed")
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = `Data_Science_Certificate_${user.name.replace(/\s+/g, '_')}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(downloadUrl)
    } catch (err) {
      console.error(err)
      alert("Could not download the certificate PDF. Please try again.")
    }
  }

  // Format date helper
  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
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

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-out' }}>
      <div className="header-bar">
        <div className="page-title-section">
          <h1 style={{ fontSize: '2rem', marginBottom: '0.25rem' }}>Student Profile</h1>
          <p className="page-subtitle">Manage your credentials, view achievements, and download certificates.</p>
        </div>
      </div>

      <div className="profile-grid">
        {/* Left Column: User info cards */}
        <div className="glass-panel profile-sidebar" style={{ alignSelf: 'start' }}>
          <div className="profile-avatar">
            {user?.name ? user.name.split(' ').map(n=>n[0]).slice(0,2).join('').toUpperCase() : 'DS'}
          </div>
          <h2 className="profile-name">{user?.name}</h2>
          <span className="profile-email">{user?.email}</span>

          <div className="profile-meta-list">
            <div className="profile-meta-item">
              <span className="profile-meta-label">Member Since</span>
              <span className="profile-meta-value">{formatDate(user?.created_at)}</span>
            </div>
            <div className="profile-meta-item">
              <span className="profile-meta-label">Current Streak</span>
              <span className="profile-meta-value" style={{ color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                <Flame size={16} fill="var(--warning)" color="var(--warning)" />
                {stats?.streak_count} Days
              </span>
            </div>
            <div className="profile-meta-item">
              <span className="profile-meta-label">Completed Weeks</span>
              <span className="profile-meta-value">{stats?.lessons_completed} / 12</span>
            </div>
            <div className="profile-meta-item">
              <span className="profile-meta-label">Score Average</span>
              <span className="profile-meta-value">{stats?.avg_quiz_score}%</span>
            </div>
          </div>
        </div>

        {/* Right Column: Achievements & Certificate */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Certificate Generation Panel */}
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Trophy size={20} color="var(--primary)" />
              <span>Official Certification</span>
            </h2>

            {certificate ? (
              /* Certificate Available for Download */
              <div className="glass-panel cert-unlocked-card shimmering">
                <div>
                  <h3 style={{ color: 'var(--secondary)', fontWeight: 700, fontSize: '1.15rem', marginBottom: '0.5rem' }}>
                    Course Certificate Generated!
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Certificate ID: <strong style={{ color: 'white', fontFamily: 'monospace' }}>{certificate.certificate_code}</strong><br />
                    Issued Date: {formatDate(certificate.issue_date)}
                  </p>
                </div>
                <button 
                  className="btn btn-primary"
                  onClick={handleDownloadCertificate}
                  style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)' }}
                >
                  <Download size={16} />
                  <span>Download Certificate PDF</span>
                </button>
              </div>
            ) : certEligible ? (
              /* Completed, needs generation */
              <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.25rem' }}>You are eligible for graduation!</h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Generate your official credential document now.</p>
                </div>
                <button 
                  className="btn btn-primary"
                  onClick={handleGenerateCertificate}
                  disabled={generatingCert}
                >
                  {generatingCert ? 'Generating...' : 'Claim Certificate'}
                </button>
              </div>
            ) : (
              /* Locked */
              <div className="glass-panel cert-locked-card">
                <Lock size={28} color="var(--text-muted)" />
                <div>
                  <h3 style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Certificate Locked ({stats?.lessons_completed}/12 Weeks Completed)
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Complete the readings, assignments, and quizzes for all 12 weeks to unlock your official Data Science Certificate.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Badges Grid Panel */}
          <div className="glass-panel badges-container">
            <div className="badges-header">
              <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Award size={20} color="var(--primary)" />
                <span>Earned Milestone Badges</span>
              </h2>
            </div>
            
            <div className="badges-grid">
              {badges.map((badge) => {
                const isUnlocked = !!badge.date_awarded
                return (
                  <div 
                    key={badge.badge_id} 
                    className={`glass-panel badge-card ${isUnlocked ? 'unlocked' : ''}`}
                    title={badge.description}
                  >
                    <div 
                      className="badge-icon-container"
                      dangerouslySetInnerHTML={{ __html: badge.icon_svg }}
                    />
                    <span className="badge-name-lbl">{badge.name}</span>
                    {isUnlocked ? (
                      <span className="badge-date-lbl">Earned {new Date(badge.date_awarded).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}</span>
                    ) : (
                      <span className="badge-date-lbl" style={{ color: 'var(--text-muted)' }}>Locked</span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
