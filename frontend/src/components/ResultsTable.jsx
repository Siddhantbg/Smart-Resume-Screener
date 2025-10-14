export default function ResultsTable({ results }) {
  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600 bg-green-50'
    if (score >= 6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getScoreBadge = (score) => {
    const rounded = Math.round(score * 10) / 10
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${getScoreColor(score)}`}>
        {rounded}/10
      </span>
    )
  }

  const shortlistedCount = results.filter((_, index) => index < 3).length

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
      {shortlistedCount > 0 && (
        <div className="bg-blue-50 border-b border-blue-100 px-6 py-3">
          <p className="text-sm font-medium text-blue-900">
            🎯 Top {shortlistedCount} candidate{shortlistedCount > 1 ? 's' : ''} shortlisted
          </p>
        </div>
      )}
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Candidate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Skills Match
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Experience
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Education
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Overall Fit
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {results.map((result, index) => (
              <tr key={index} className={index < 3 ? 'bg-blue-50' : 'hover:bg-slate-50'}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className={`text-lg font-bold ${index < 3 ? 'text-blue-600' : 'text-slate-400'}`}>
                      #{index + 1}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-slate-900">
                    {result.candidate_name}
                  </div>
                  <div className="text-xs text-slate-500">
                    {result.resumeName}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getScoreBadge(result.skills_match)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getScoreBadge(result.experience_relevance)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getScoreBadge(result.education_fit)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold ${getScoreColor(result.overall_fit)}`}>
                    {Math.round(result.overall_fit * 10) / 10}/10
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {index < 3 ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                      Shortlisted
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
                      Under Review
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
