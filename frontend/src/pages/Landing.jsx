import { useNavigate } from 'react-router-dom'
import Ballpit from '../components/Ballpit'

export default function Landing() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    navigate('/home')
  }

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden', background: '#0a0a0a' }}>
      {/* Credits Badge */}
      <div style={{
        position: 'absolute',
        top: '24px',
        left: '24px',
        zIndex: 20,
        backgroundColor: 'rgba(255,255,255,0.08)',
        backdropFilter: 'blur(12px)',
        padding: '16px 24px',
        borderRadius: '16px',
        border: '1px solid rgba(255,255,255,0.15)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)'
      }}>
        <p style={{
          color: 'white',
          fontSize: '0.9rem',
          margin: 0,
          lineHeight: '1.5',
          fontWeight: '400'
        }}>
          <strong style={{ fontSize: '1rem' }}>Siddhant Bhagat</strong><br/>
          <span style={{ color: 'rgba(255,255,255,0.8)' }}>VIT Vellore</span><br/>
          <span style={{ color: 'rgba(139,92,246,0.9)', fontSize: '0.85rem', fontWeight: '500' }}>
            Assignment for Unthinkable
          </span>
        </p>
      </div>

      <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
        <Ballpit
          count={200}
          gravity={0.3}
          friction={0.985}
          wallBounce={0.98}
          maxVelocity={0.12}
          followCursor={true}
          colors={[0x3b82f6, 0x8b5cf6, 0xec4899]}
        />
      </div>

      <div style={{ position: 'relative', zIndex: 10, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
        <div style={{ maxWidth: '900px', textAlign: 'center', color: 'white' }}>
          <h1 style={{ 
            fontSize: 'clamp(2.5rem, 8vw, 5.5rem)', 
            fontWeight: '900', 
            marginBottom: '1.5rem', 
            lineHeight: '1.1', 
            letterSpacing: '-0.02em', 
            textShadow: '0 8px 32px rgba(0,0,0,0.8), 0 4px 16px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.4)',
            color: '#ffffff',
            WebkitTextStroke: '1px rgba(0,0,0,0.1)'
          }}>
            Smart Resume Screener
          </h1>
          <p style={{ 
            fontSize: 'clamp(1.125rem, 2.5vw, 1.5rem)', 
            marginBottom: '1rem', 
            fontWeight: '600', 
            textShadow: '0 6px 24px rgba(0,0,0,0.8), 0 3px 12px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.4)', 
            color: '#ffffff',
            backgroundColor: 'rgba(0,0,0,0.3)',
            padding: '0.5rem 1.5rem',
            borderRadius: '12px',
            display: 'inline-block'
          }}>
            AI-Powered Candidate Evaluation & Intelligent Ranking
          </p>
          <p style={{ 
            fontSize: 'clamp(0.95rem, 2vw, 1.125rem)', 
            marginBottom: '3rem', 
            fontWeight: '400', 
            lineHeight: '1.6', 
            textShadow: '0 6px 24px rgba(0,0,0,0.9), 0 3px 12px rgba(0,0,0,0.7), 0 2px 6px rgba(0,0,0,0.5)', 
            color: '#ffffff',
            maxWidth: '700px', 
            margin: '1.5rem auto 3rem',
            backgroundColor: 'rgba(0,0,0,0.25)',
            padding: '1rem 2rem',
            borderRadius: '12px',
            backdropFilter: 'blur(8px)'
          }}>
            Upload resumes, analyze job descriptions, and get instant intelligent scores with context-aware shortlisting based on seniority levels and skill matching.
          </p>
          <button
            onClick={handleGetStarted}
            style={{
              padding: '1.1rem 3.5rem',
              fontSize: '1.125rem',
              fontWeight: '600',
              color: '#ffffff',
              background: 'rgba(255, 255, 255, 0.12)',
              backdropFilter: 'blur(12px)',
              border: '2px solid rgba(255, 255, 255, 0.25)',
              borderRadius: '16px',
              cursor: 'pointer',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.15)',
              transform: 'scale(1)',
              letterSpacing: '0.5px'
            }}
            onMouseEnter={e => {
              e.target.style.transform = 'translateY(-2px) scale(1.02)'
              e.target.style.background = 'rgba(255, 255, 255, 0.18)'
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.35)'
              e.target.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
            }}
            onMouseLeave={e => {
              e.target.style.transform = 'scale(1)'
              e.target.style.background = 'rgba(255, 255, 255, 0.12)'
              e.target.style.borderColor = 'rgba(255, 255, 255, 0.25)'
              e.target.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.15)'
            }}
          >
            Get Started
          </button>
        </div>
      </div>
    </div>
  )
}
