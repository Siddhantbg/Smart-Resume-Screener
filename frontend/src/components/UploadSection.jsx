import { useState, useEffect } from 'react'
import axios from 'axios'

export default function UploadSection({ setResults, setLoading, setError }) {
  const [resumes, setResumes] = useState([])
  const [jobDescription, setJobDescription] = useState(null)
  const [uploadedResumes, setUploadedResumes] = useState([])
  const [loadingUploaded, setLoadingUploaded] = useState(false)

  // Fetch uploaded resumes on component mount
  useEffect(() => {
    fetchUploadedResumes()
  }, [])

  const fetchUploadedResumes = async () => {
    setLoadingUploaded(true)
    try {
      const response = await axios.get('/api/resumes')
      // API returns { status, count, data } - extract the data array
      setUploadedResumes(response.data.data || [])
    } catch (err) {
      console.error('Error fetching uploaded resumes:', err)
      setUploadedResumes([]) // Set empty array on error
    } finally {
      setLoadingUploaded(false)
    }
  }

  const handleResumeChange = (e) => {
    const files = Array.from(e.target.files)
    setResumes(files)
  }

  const handleJDChange = (e) => {
    setJobDescription(e.target.files[0])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (resumes.length === 0 || !jobDescription) {
      setError('Please upload at least one resume and a job description')
      return
    }

    setLoading(true)
    setError(null)
    setResults([])

    try {
      const allResults = []

      for (const resume of resumes) {
        const formData = new FormData()
        formData.append('resume', resume)
        formData.append('jd', jobDescription)

        const response = await axios.post('/api/score_files', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (response.data.status === 'success') {
          allResults.push({
            ...response.data,
            resumeName: resume.name
          })
        }
      }

      const sortedResults = allResults.sort((a, b) => b.overall_fit - a.overall_fit)
      setResults(sortedResults)
      
      // Refresh the uploaded resumes list
      fetchUploadedResumes()
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
      fetchUploadedResumes()
    } catch (err) {
      console.error('Error deleting resume:', err)
    }
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
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Job Description <span className="text-red-500">*</span>
          </label>
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
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 shadow-sm"
        >
          Analyze Candidates
        </button>
      </form>

      {/* Previously Uploaded Resumes Section */}
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

        {loadingUploaded ? (
          <div className="text-center py-8 text-slate-500">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p className="mt-2">Loading resumes...</p>
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
                    <p className="text-sm font-semibold text-slate-900 truncate">
                      {resume.name || 'Unknown Candidate'}
                    </p>
                    <p className="text-xs text-slate-600 truncate">
                      {resume.filename}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {resume.email || 'No email'} • Uploaded {formatDate(resume.timestamp)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteResume(resume._id)}
                  className="flex-shrink-0 ml-4 text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition"
                  title="Delete resume"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
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
    </div>
  )
}
