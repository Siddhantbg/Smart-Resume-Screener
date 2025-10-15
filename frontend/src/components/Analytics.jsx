import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

export default function Analytics({ refreshTrigger }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics(true); 
  }, [refreshTrigger]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchAnalytics(false); 
    }, 30000); 
    
    return () => clearInterval(intervalId);
  }, []);

  const fetchAnalytics = async (showLoading = false) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const response = await axios.get('/api/analytics');
      setAnalytics(response.data.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
      console.error('Analytics error:', err);
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error}</p>
        <button
          onClick={fetchAnalytics}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center text-gray-600">
        No analytics data available yet. Upload some resumes to see insights!
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-1">Total Resumes</h3>
          <p className="text-3xl font-bold text-blue-600">{analytics.total_resumes}</p>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-green-900 mb-1">Total Scores</h3>
          <p className="text-3xl font-bold text-green-600">{analytics.total_scores}</p>
        </div>
        
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-purple-900 mb-1">Avg Skills Match</h3>
          <p className="text-3xl font-bold text-purple-600">{analytics.average_scores.skills_match}/10</p>
        </div>
        
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-orange-900 mb-1">Avg Overall Fit</h3>
          <p className="text-3xl font-bold text-orange-600">{analytics.average_scores.overall_fit}/10</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Top Skills Distribution</h3>
          {analytics.top_skills.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics.top_skills}
                  dataKey="count"
                  nameKey="skill"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.skill} (${entry.count})`}
                >
                  {analytics.top_skills.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No skill data available</p>
          )}
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Average Fit by Role</h3>
          {analytics.fit_by_role.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.fit_by_role}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="role" angle={-45} textAnchor="end" height={100} />
                <YAxis domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg_fit" fill="#3B82F6" name="Average Fit" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No role data available</p>
          )}
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Submissions Over Time</h3>
        {analytics.submissions_over_time.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.submissions_over_time}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#10B981" strokeWidth={2} name="Submissions" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-500 text-center py-8">No submission history available</p>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Most Requested Roles</h3>
        
        {analytics.most_requested_roles.some(role => role.role === "Not specified") && (
          <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-semibold text-yellow-800 mb-1">
                  ⚠️ Old Data Detected
                </p>
                <p className="text-xs text-yellow-700 mb-2">
                  Some job titles show "Not specified" because they were uploaded before the parser was improved.
                </p>
                <p className="text-xs text-yellow-700 font-medium">
                  💡 To fix: Go to <span className="font-bold">Database tab</span> → Delete old job descriptions → Re-upload them
                </p>
              </div>
            </div>
          </div>
        )}
        
        {analytics.most_requested_roles.length > 0 ? (
          <div className="space-y-2">
            {analytics.most_requested_roles.map((role, index) => (
              <div 
                key={index} 
                className={`mt-8 rounded-lg p-4 ${
                  role.role === "Not specified" 
                    ? "bg-yellow-50 border border-yellow-200" 
                    : "bg-gray-50"
                }`}
                style={{
                  background: 'linear-gradient(135deg, rgba(59,130,246,0.12), rgba(139,92,246,0.12))',
                  border: '1px solid rgba(139,92,246,0.18)',
                  boxShadow: '0 2px 16px rgba(139,92,246,0.10)',
                  color: '#fff',
                  fontWeight: 500,
                  fontSize: '1.25rem',
                  letterSpacing: '0.5px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <span style={{ color: '#fff', fontWeight: 600 }}>
                  {role.role}
                </span>
                <span style={{
                  background: 'linear-gradient(135deg, rgba(59,130,246,0.25), rgba(139,92,246,0.25))',
                  color: '#fff',
                  fontWeight: 600,
                  borderRadius: '999px',
                  padding: '0.5rem 1.25rem',
                  fontSize: '1rem',
                  boxShadow: '0 2px 8px rgba(139,92,246,0.15)'
                }}>
                  {role.count} requests
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No role requests yet</p>
        )}
      </div>

      <div className="flex justify-end">
        <button
          onClick={fetchAnalytics}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Refresh Analytics
        </button>
      </div>
    </div>
  );
}
