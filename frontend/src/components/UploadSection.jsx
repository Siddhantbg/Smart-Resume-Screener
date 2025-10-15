import { useState, useEffect } from 'react'
import axios from 'axios'
import StatusLottie from './StatusLottie'
import StatusIcon from './StatusIcon'

export default function UploadSection({ setResults, setLoading, setError }) {
  const [resumes, setResumes] = useState([])
  const [jobDescription, setJobDescription] = useState(null)
  const [uploadedResumes, setUploadedResumes] = useState([])
  const [loadingUploaded, setLoadingUploaded] = useState(true) 
  const [selectedResume, setSelectedResume] = useState(null)
  const [resumeScores, setResumeScores] = useState([])
  const [loadingScores, setLoadingScores] = useState(false)
  const [uploadedJDs, setUploadedJDs] = useState([])
  const [loadingJDs, setLoadingJDs] = useState(true)
  const [selectedJDId, setSelectedJDId] = useState('')
  const [jdMode, setJdMode] = useState('upload') 
  const [resumeStatuses, setResumeStatuses] = useState({}) 

  useEffect(() => {
    fetchUploadedResumes()
    fetchUploadedJDs()
  }, [])

  const fetchUploadedResumes = async () => {
    setLoadingUploaded(true)
    try {
      const response = await axios.get('/api/resumes')
      const resumesData = response.data.data || []
      setUploadedResumes(resumesData)
      
      // If no resumes, clear cached results
      if (resumesData.length === 0) {
        try {
          localStorage.removeItem('srs:lastResults:v1')
          if (typeof setResults === 'function') {
            setResults([])
          }
        } catch {}
      }
      
      await fetchResumeStatuses(resumesData)
    } catch (err) {
      console.error('Error fetching uploaded resumes:', err)
      setUploadedResumes([])
      // Clear results on error too
      try {
        localStorage.removeItem('srs:lastResults:v1')
        if (typeof setResults === 'function') {
          setResults([])
        }
      } catch {}
    } finally {
      setLoadingUploaded(false)
    }
  }

  const fetchResumeStatuses = async (resumesData) => {
    try {
      const statuses = {}
      
      for (const resume of resumesData) {
        try {
          const scoresResponse = await axios.get(`/api/resumes/${resume._id}/scores`)
          const scores = scoresResponse.data.data || []
          
          if (scores.length > 0) {
            const latestScore = [...scores]
              .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]
            statuses[resume._id] = {
              is_shortlisted: !!latestScore.is_shortlisted,
              overall_fit: Number.parseFloat(latestScore.overall_fit) || 0,
              skills_match: Number.parseFloat(latestScore.skills_match) || 0,
              experience_relevance: Number.parseFloat(latestScore.experience_relevance) || 0,
              education_fit: Number.parseFloat(latestScore.education_fit) || 0,
              seniority_level: latestScore.seniority_level,
              job_title: latestScore.job_title,
              timestamp: latestScore.timestamp
            }
          }
        } catch (err) {
          console.error(`Error fetching scores for resume ${resume._id}:`, err)
        }
      }
      
      setResumeStatuses(statuses)

      try {
        const byKey = new Map()
        for (const r of resumesData) {
          const s = statuses[r._id]
          if (!s) continue
          const key = (r.email?.toLowerCase() || '').trim() || (r.filename || '').trim() || (r.name || '').trim()
          const item = {
            id: r._id,
            candidate_name: r.name || r.email || 'Unknown Candidate',
            resumeName: r.filename || '',
            email: r.email || '',
            skills_match: Number(s.skills_match) || 0,
            experience_relevance: Number(s.experience_relevance) || 0,
            education_fit: Number(s.education_fit) || 0,
            overall_fit: Number(s.overall_fit) || 0,
            seniority_level: s.seniority_level || 'Unknown',
            job_title: s.job_title || '',
            is_shortlisted: s.is_shortlisted || (s.overall_fit >= 7.0),
          }
          const prev = byKey.get(key)
          if (!prev || (item.overall_fit ?? 0) > (prev.overall_fit ?? 0)) {
            byKey.set(key, item)
          }
        }

        const assembled = Array.from(byKey.values()).sort((a, b) => b.overall_fit - a.overall_fit)

        if (assembled.length > 0 && typeof setResults === 'function') {
          setResults(assembled)
        }
      } catch (e) {
      }
    } catch (err) {
      console.error('Error fetching resume statuses:', err)
    }
  }

  const fetchUploadedJDs = async () => {
    setLoadingJDs(true)
    try {
      const response = await axios.get('/api/job_descriptions')
      setUploadedJDs(response.data.data || [])
    } catch (err) {
      console.error('Error fetching job descriptions:', err)
      setUploadedJDs([])
    } finally {
      setLoadingJDs(false)
    }
  }

  const handleResumeChange = (e) => {
    const files = Array.from(e.target.files)
    setResumes(files)
  }

  const handleJDChange = (e) => {
    setJobDescription(e.target.files[0])
    setSelectedJDId('')
  }

  const handleJDModeChange = (mode) => {
    setJdMode(mode)
    if (mode === 'upload') {
      setSelectedJDId('')
    } else {
      setJobDescription(null)
    }
  }

  const handleSelectJD = (e) => {
    setSelectedJDId(e.target.value)
    setJobDescription(null) 
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validate inputs based on mode
    if (resumes.length === 0) {
      setError('Please upload at least one resume')
      return
    }

    if (jdMode === 'upload' && !jobDescription) {
      setError('Please upload a job description')
      return
    }

    if (jdMode === 'select' && !selectedJDId) {
      setError('Please select a job description from the dropdown')
      return
    }

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const allResults = []

      for (const resume of resumes) {
        let response

        if (jdMode === 'select') {
          const formData = new FormData()
          formData.append('resume', resume)
          formData.append('jd_id', selectedJDId)

          response = await axios.post('/api/score_with_existing_jd', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        } else {
          const formData = new FormData()
          formData.append('resume', resume)
          formData.append('jd', jobDescription)

          response = await axios.post('/api/score_files', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        }

        if (response.data.status === 'success') {
          allResults.push({
            ...response.data,
            resumeName: resume.name
          })
        }
      }

      const sortedResults = allResults.sort((a, b) => b.overall_fit - a.overall_fit)
      setResults(sortedResults)
      
      fetchUploadedResumes()
      fetchUploadedJDs()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process files. Please check your API key and try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteResume = async (id) => {
    if (!confirm('Delete this resume? This will also delete all associated scores.')) {
      return
    }
    
    try {
      await axios.delete(`/api/resumes/${id}`)
      
      // Clear selected resume if it's the one being deleted
      if (selectedResume && selectedResume._id === id) {
        setSelectedResume(null)
        setResumeScores([])
      }
      
      // Refetch resumes which will auto-clear results if empty
      await fetchUploadedResumes()
    } catch (err) {
      console.error('Error deleting resume:', err)
    }
  }

  const handleViewStats = async (resume) => {
    setSelectedResume(resume)
    setLoadingScores(true)
    try {
      const response = await axios.get(`/api/resumes/${resume._id}/scores`)
      setResumeScores(response.data.data || [])
    } catch (err) {
      console.error('Error fetching resume scores:', err)
      setResumeScores([])
    } finally {
      setLoadingScores(false)
    }
  }

  const closeStatsModal = () => {
    setSelectedResume(null)
    setResumeScores([])
  }

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (resumeId) => {
    const status = resumeStatuses[resumeId]
    
    if (!status) {
      return (
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">
          Not Evaluated
        </span>
      )
    }

   
    if (status.is_shortlisted || status.overall_fit >= 7.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
          <StatusIcon type="shortlisted" className="w-4 h-4" title="Shortlisted" />
          Shortlisted
        </span>
      )
    } else if (status.overall_fit >= 6.5) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800">
          <StatusIcon type="review" className="w-4 h-4" title="Waitlisted" />
          Waitlisted
        </span>
      )
    } else {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800">
          <StatusIcon type="rejected" className="w-4 h-4" title="Rejected" />
          Rejected
        </span>
      )
    }
  }

  const getStatusDetails = (resumeId) => {
    const status = resumeStatuses[resumeId]
    if (!status) return null

    return (
      <div className="text-xs text-slate-500 mt-1.5">
        <span className="font-medium">Score: {status.overall_fit.toFixed(1)}/10</span>
        {status.job_title && (
          <span className="ml-2">• Last evaluated for: {status.job_title}</span>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">Upload Documents</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Resume(s) <span className="text-red-500">*</span>
          </label>
          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={handleResumeChange}
            className="block w-full text-sm text-slate-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100 cursor-pointer"
          />
          {resumes.length > 0 && (
            <p className="mt-2 text-sm text-slate-600">
              {resumes.length} file(s) selected
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-3">
            Job Description <span className="text-red-500">*</span>
          </label>
          
          {/* Mode Toggle */}
          <div className="flex gap-2 mb-3">
            <button
              type="button"
              onClick={() => handleJDModeChange('upload')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition ${
                jdMode === 'upload'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Upload New JD
            </button>
            <button
              type="button"
              onClick={() => handleJDModeChange('select')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition ${
                jdMode === 'select'
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              Select Existing JD
            </button>
          </div>

          {/* Upload Mode */}
          {jdMode === 'upload' && (
            <>
              <input
                type="file"
                accept=".pdf"
                onChange={handleJDChange}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100 cursor-pointer"
              />
              {jobDescription && (
                <p className="mt-2 text-sm text-slate-600">
                  {jobDescription.name}
                </p>
              )}
            </>
          )}

          {jdMode === 'select' && (
            <div>
              {loadingJDs ? (
                <div className="text-center py-4 text-slate-500">
                  <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                  <p className="mt-2 text-sm">Loading job descriptions...</p>
                </div>
              ) : uploadedJDs.length === 0 ? (
                <div className="text-center py-4 text-slate-500 bg-slate-50 rounded-lg border border-slate-200">
                  <p className="text-sm">No job descriptions uploaded yet</p>
                  <p className="text-xs mt-1">Switch to "Upload New JD" to add one</p>
                </div>
              ) : (
                <>
                  <select
                    value={selectedJDId}
                    onChange={handleSelectJD}
                    className="block w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">-- Select a Job Description --</option>
                    {uploadedJDs.map((jd) => (
                      <option key={jd._id} value={jd._id}>
                        {jd.job_title || 'Unknown Position'} - {jd.company || 'No Company'} ({new Date(jd.timestamp).toLocaleDateString()})
                      </option>
                    ))}
                  </select>
                  {selectedJDId && (
                    <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-900 font-medium">
                        Selected: {uploadedJDs.find(jd => jd._id === selectedJDId)?.job_title || 'Unknown'}
                      </p>
                      <p className="text-xs text-blue-700 mt-1">
                        {uploadedJDs.find(jd => jd._id === selectedJDId)?.filename}
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 shadow-sm"
        >
          Analyze Candidates
        </button>
      </form>

      <div className="mt-8 border-t border-slate-200 pt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-900">
            Previously Uploaded Resumes
          </h3>
          <button
            onClick={fetchUploadedResumes}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>

        {uploadedResumes.length > 0 && Object.keys(resumeStatuses).length > 0 && (
          <div className="grid grid-cols-4 gap-3 mb-4">
            <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
              <p className="text-xs text-slate-600 font-medium mb-1">Total Resumes</p>
              <p className="text-2xl font-bold text-slate-900">{uploadedResumes.length}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-3 border border-green-200">
              <p className="text-xs text-green-700 font-medium mb-1 inline-flex items-center gap-1">
                <span className="text-green-700"><StatusIcon type="shortlisted" className="w-4 h-4" title="Shortlisted" /></span>
                Shortlisted
              </p>
              <p className="text-2xl font-bold text-green-800">
                {Object.values(resumeStatuses).filter(s => s.is_shortlisted || s.overall_fit >= 7.0).length}
              </p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
              <p className="text-xs text-yellow-700 font-medium mb-1 inline-flex items-center gap-1">
                <span className="text-yellow-700"><StatusIcon type="review" className="w-4 h-4" title="Waitlisted" /></span>
                Waitlisted
              </p>
              <p className="text-2xl font-bold text-yellow-800">
                {Object.values(resumeStatuses).filter(s => !s.is_shortlisted && s.overall_fit >= 6.5 && s.overall_fit < 7.5).length}
              </p>
            </div>
            <div className="bg-red-50 rounded-lg p-3 border border-red-200">
              <p className="text-xs text-red-700 font-medium mb-1 inline-flex items-center gap-1">
                <span className="text-red-700"><StatusIcon type="rejected" className="w-4 h-4" title="Rejected" /></span>
                Rejected
              </p>
              <p className="text-2xl font-bold text-red-800">
                {Object.values(resumeStatuses).filter(s => s.overall_fit < 6.5).length}
              </p>
            </div>
          </div>
        )}

        {loadingUploaded ? (
          <div className="flex flex-col items-center justify-center py-16 bg-slate-50 rounded-lg border border-slate-200">
            <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-slate-200 border-t-blue-500"></div>
            <p className="mt-4 text-sm font-medium text-slate-600">Loading resumes...</p>
          </div>
        ) : uploadedResumes.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <svg className="mx-auto h-12 w-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="mt-2">No resumes uploaded yet</p>
            <p className="text-sm mt-1">Upload your first resume to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {uploadedResumes.map((resume) => (
              <div
                key={resume._id}
                className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition"
              >
                <div className="flex items-center gap-3 flex-1">
                  <div className="flex-shrink-0">
                    <svg className="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-semibold text-slate-900 truncate">
                        {resume.name || 'Unknown Candidate'}
                      </p>
                      {getStatusBadge(resume._id)}
                    </div>
                    <p className="text-xs text-slate-600 truncate">
                      {resume.filename}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {resume.email || 'No email'} • Uploaded {formatDate(resume.timestamp)}
                    </p>
                    {getStatusDetails(resume._id)}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleViewStats(resume)}
                    className="flex-shrink-0 text-blue-600 hover:text-blue-700 p-2 hover:bg-blue-50 rounded-lg transition"
                    title="View scoring history"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDeleteResume(resume._id)}
                    className="flex-shrink-0 text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition"
                    title="Delete resume"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {uploadedResumes.length > 0 && (
          <div className="mt-4 text-sm text-slate-600 text-center">
            Total: {uploadedResumes.length} resume{uploadedResumes.length !== 1 ? 's' : ''} stored
          </div>
        )}
      </div>

      {selectedResume && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <div>
                <h3 className="text-xl font-semibold text-slate-900">
                  {selectedResume.name || 'Unknown Candidate'}
                </h3>
                <p className="text-sm text-slate-600 mt-1">
                  {selectedResume.filename} • {selectedResume.email || 'No email'}
                </p>
              </div>
              <button
                onClick={closeStatsModal}
                className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-100 rounded-lg transition"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {loadingScores ? (
                <div className="text-center py-12">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  <p className="mt-4 text-slate-600">Loading scoring history...</p>
                </div>
              ) : resumeScores.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-16 w-16 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="mt-4 text-slate-600 font-medium">No scoring history found</p>
                  <p className="text-sm text-slate-500 mt-2">This resume hasn't been scored against any job descriptions yet.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-sm text-blue-600 font-medium">Total Evaluations</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">{resumeScores.length}</p>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                      <p className="text-sm text-green-600 font-medium">Avg Overall Fit</p>
                      <p className="text-2xl font-bold text-green-900 mt-1">
                        {(resumeScores.reduce((sum, s) => sum + s.overall_fit, 0) / resumeScores.length).toFixed(1)}/10
                      </p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-4">
                      <p className="text-sm text-purple-600 font-medium">Best Match</p>
                      <p className="text-2xl font-bold text-purple-900 mt-1">
                        {Math.max(...resumeScores.map(s => s.overall_fit)).toFixed(1)}/10
                      </p>
                    </div>
                    <div className="bg-amber-50 rounded-lg p-4">
                      <p className="text-sm text-amber-600 font-medium">Avg Skills Match</p>
                      <p className="text-2xl font-bold text-amber-900 mt-1">
                        {(resumeScores.reduce((sum, s) => sum + s.skills_match, 0) / resumeScores.length).toFixed(1)}/10
                      </p>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-lg font-semibold text-slate-900 mb-4">Scoring History</h4>
                    <div className="space-y-4">
                      {resumeScores.map((score, index) => (
                        <div key={score._id} className="bg-slate-50 rounded-lg border border-slate-200 p-5">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h5 className="font-semibold text-slate-900">
                                {score.job_title || 'Unknown Position'}
                              </h5>
                              <p className="text-sm text-slate-600 mt-1">
                                Evaluated on {formatDate(score.timestamp)}
                              </p>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-blue-600">
                                {score.overall_fit}/10
                              </div>
                              <p className="text-xs text-slate-500">Overall Fit</p>
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-4 mb-4">
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-slate-600">Skills Match</span>
                                <span className="text-sm font-semibold text-slate-900">{score.skills_match}/10</span>
                              </div>
                              <div className="w-full bg-slate-200 rounded-full h-2">
                                <div
                                  className="bg-blue-500 h-2 rounded-full transition-all"
                                  style={{ width: `${(score.skills_match / 10) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-slate-600">Experience</span>
                                <span className="text-sm font-semibold text-slate-900">{score.experience_relevance}/10</span>
                              </div>
                              <div className="w-full bg-slate-200 rounded-full h-2">
                                <div
                                  className="bg-green-500 h-2 rounded-full transition-all"
                                  style={{ width: `${(score.experience_relevance / 10) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                            <div>
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm text-slate-600">Education</span>
                                <span className="text-sm font-semibold text-slate-900">{score.education_fit}/10</span>
                              </div>
                              <div className="w-full bg-slate-200 rounded-full h-2">
                                <div
                                  className="bg-purple-500 h-2 rounded-full transition-all"
                                  style={{ width: `${(score.education_fit / 10) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>

                          {score.justification && (
                            <div className="bg-white rounded-lg p-4 border border-slate-200">
                              <p className="text-xs font-medium text-slate-500 uppercase mb-2">AI Analysis</p>
                              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                                {score.justification}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
