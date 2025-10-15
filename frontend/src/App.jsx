import { useState } from 'react'
import UploadSection from './components/UploadSection'
import ResultsTable from './components/ResultsTable'
import ScoreCard from './components/ScoreCard'
import Analytics from './components/Analytics'
import DatabaseManager from './components/DatabaseManager'

function App() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [viewMode, setViewMode] = useState('table')
  const [activeTab, setActiveTab] = useState('upload')
  const [analyticsRefreshTrigger, setAnalyticsRefreshTrigger] = useState(0)

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-slate-900">Smart Resume Screener</h1>
          <p className="mt-1 text-sm text-slate-600">AI-powered candidate evaluation and ranking</p>
          
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === 'upload'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Upload & Score
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === 'analytics'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('database')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === 'database'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
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
              setResults={setResults}
              setLoading={setLoading}
              setError={setError}
            />

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            {loading && (
              <div className="mt-8 flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              </div>
            )}

            {results.length > 0 && !loading && (
              <div className="mt-8">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-slate-900">
                    Results ({results.length} candidates)
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setViewMode('table')}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        viewMode === 'table'
                          ? 'bg-blue-500 text-white'
                          : 'bg-white text-slate-700 hover:bg-slate-100'
                      }`}
                    >
                      Table View
                    </button>
                    <button
                      onClick={() => setViewMode('card')}
                      className={`px-4 py-2 rounded-lg font-medium transition ${
                        viewMode === 'card'
                          ? 'bg-blue-500 text-white'
                          : 'bg-white text-slate-700 hover:bg-slate-100'
                      }`}
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

export default App
