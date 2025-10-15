import { useEffect, useState } from 'react'
import UploadSection from '../components/UploadSection'
import ResultsTable from '../components/ResultsTable'
import ScoreCard from '../components/ScoreCard'
import Analytics from '../components/Analytics'
import DatabaseManager from '../components/DatabaseManager'

function Home() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [viewMode, setViewMode] = useState('table')
  const [activeTab, setActiveTab] = useState('upload')
  const [analyticsRefreshTrigger, setAnalyticsRefreshTrigger] = useState(0)

  const RESULTS_KEY = 'srs:lastResults:v1'
  const VIEWMODE_KEY = 'srs:viewMode:v1'

  useEffect(() => {
    try {
      const cached = localStorage.getItem(RESULTS_KEY)
      if (cached) {
        const parsed = JSON.parse(cached)
        if (parsed && Array.isArray(parsed.results)) {
          setResults(parsed.results)
        }
      }
    } catch {}

    try {
      const cachedView = localStorage.getItem(VIEWMODE_KEY)
      if (cachedView === 'table' || cachedView === 'card') {
        setViewMode(cachedView)
      }
    } catch {}
  }, [])

  const handleSetResults = (newResults) => {
    setResults(newResults)
    try {
      localStorage.setItem(RESULTS_KEY, JSON.stringify({ ts: Date.now(), results: newResults }))
    } catch {}
  }

  const handleSetViewMode = (mode) => {
    setViewMode(mode)
    try {
      localStorage.setItem(VIEWMODE_KEY, mode)
    } catch {}
  }

  return (
    <div className="min-h-screen" style={{ background: '#0a0a0a' }}>
      <header style={{ 
        background: 'rgba(255, 255, 255, 0.05)', 
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)'
      }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold" style={{ color: '#ffffff' }}>Smart Resume Screener</h1>
          <p className="mt-1 text-sm" style={{ color: 'rgba(255, 255, 255, 0.7)' }}>AI-powered candidate evaluation and ranking</p>
          
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => setActiveTab('upload')}
              className="px-4 py-2 rounded-lg font-medium transition"
              style={activeTab === 'upload' ? {
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.25)',
                color: '#ffffff'
              } : {
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.7)'
              }}
            >
              Upload & Score
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className="px-4 py-2 rounded-lg font-medium transition"
              style={activeTab === 'analytics' ? {
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.25)',
                color: '#ffffff'
              } : {
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.7)'
              }}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('database')}
              className="px-4 py-2 rounded-lg font-medium transition"
              style={activeTab === 'database' ? {
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.25)',
                color: '#ffffff'
              } : {
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.7)'
              }}
            >
              Database
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'upload' ? (
          <>
            <UploadSection 
              setResults={handleSetResults}
              setLoading={setLoading}
              setError={setError}
            />

            {error && (
              <div className="mt-6 px-4 py-3 rounded-lg" style={{
                background: 'rgba(239, 68, 68, 0.15)',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#fca5a5'
              }}>
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {loading && (
              <div className="mt-8 flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12" style={{ borderBottom: '2px solid rgba(139, 92, 246, 0.8)' }}></div>
              </div>
            )}

            {results.length > 0 && !loading && (
              <div className="mt-8">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold" style={{ color: '#ffffff' }}>
                    Results ({results.length} candidates)
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSetViewMode('table')}
                      className="px-4 py-2 rounded-lg font-medium transition"
                      style={viewMode === 'table' ? {
                        background: 'rgba(255, 255, 255, 0.15)',
                        backdropFilter: 'blur(8px)',
                        border: '1px solid rgba(255, 255, 255, 0.25)',
                        color: '#ffffff'
                      } : {
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        color: 'rgba(255, 255, 255, 0.7)'
                      }}
                    >
                      Table View
                    </button>
                    <button
                      onClick={() => handleSetViewMode('card')}
                      className="px-4 py-2 rounded-lg font-medium transition"
                      style={viewMode === 'card' ? {
                        background: 'rgba(255, 255, 255, 0.15)',
                        backdropFilter: 'blur(8px)',
                        border: '1px solid rgba(255, 255, 255, 0.25)',
                        color: '#ffffff'
                      } : {
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        color: 'rgba(255, 255, 255, 0.7)'
                      }}
                    >
                      Card View
                    </button>
                  </div>
                </div>

                {viewMode === 'table' ? (
                  <ResultsTable results={results} />
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {results.map((result, index) => (
                      <ScoreCard key={index} result={result} rank={index + 1} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        ) : activeTab === 'analytics' ? (
          <Analytics refreshTrigger={analyticsRefreshTrigger} />
        ) : (
          <DatabaseManager onDataChange={() => setAnalyticsRefreshTrigger(prev => prev + 1)} />
        )}
      </main>
    </div>
  )
}

export default Home
