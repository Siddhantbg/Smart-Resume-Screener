export default function ScoreCard({ result, rank }) {
  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getProgressColor = (score) => {
    if (score >= 8) return 'bg-green-500'
    if (score >= 6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const SHORTLIST_THRESHOLD = 6.0
  const isShortlisted = result.overall_fit >= SHORTLIST_THRESHOLD && rank <= 3

  const getStatusBadge = () => {
    if (isShortlisted) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">
          Shortlisted
        </span>
      )
    }
    if (result.overall_fit >= 4) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-800">
          Under Review
        </span>
      )
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">
        Not Qualified
      </span>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border-2 ${isShortlisted ? 'border-blue-500' : 'border-slate-200'} p-6`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className={`text-2xl font-bold ${isShortlisted ? 'text-blue-600' : 'text-slate-400'}`}>
              #{rank}
            </span>
            {getStatusBadge()}
          </div>
          <h3 className="text-xl font-bold text-slate-900 mt-2">
            {result.candidate_name}
          </h3>
          <p className="text-sm text-slate-500 mt-1">{result.job_title}</p>
        </div>
        <div className={`text-4xl font-bold ${getScoreColor(result.overall_fit)}`}>
          {Math.round(result.overall_fit * 10) / 10}
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-600">Skills Match</span>
            <span className="font-semibold">{Math.round(result.skills_match * 10) / 10}/10</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressColor(result.skills_match)}`}
              style={{ width: `${(result.skills_match / 10) * 100}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-600">Experience Relevance</span>
            <span className="font-semibold">{Math.round(result.experience_relevance * 10) / 10}/10</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressColor(result.experience_relevance)}`}
              style={{ width: `${(result.experience_relevance / 10) * 100}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-600">Education Fit</span>
            <span className="font-semibold">{Math.round(result.education_fit * 10) / 10}/10</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getProgressColor(result.education_fit)}`}
              style={{ width: `${(result.education_fit / 10) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 pt-4">
        <h4 className="text-sm font-semibold text-slate-700 mb-2">AI Justification</h4>
        <p className="text-sm text-slate-600 leading-relaxed">
          {result.justification}
        </p>
      </div>
    </div>
  )
}
