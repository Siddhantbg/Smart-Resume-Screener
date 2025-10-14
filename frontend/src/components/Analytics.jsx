import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/analytics');
      setAnalytics(response.data.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
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
        {analytics.most_requested_roles.length > 0 ? (
          <div className="space-y-2">
            {analytics.most_requested_roles.map((role, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                <span className="font-medium text-gray-700">{role.role}</span>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
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
