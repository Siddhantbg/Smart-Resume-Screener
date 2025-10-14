import { useState } from 'react'
import axios from 'axios'

export default function UploadSection({ setResults, setLoading, setError }) {
  const [resumes, setResumes] = useState([])
  const [jobDescription, setJobDescription] = useState(null)

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
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process files. Please check your API key and try again.')
    } finally {
      setLoading(false)
    }
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
    </div>
  )
}
