import { useState, useEffect } from 'react';
import axios from 'axios';

export default function DatabaseManager({ onDataChange }) {
  const [dbStatus, setDbStatus] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('status');

  useEffect(() => {
    fetchDbStatus();
  }, []);

  const fetchDbStatus = async () => {
    try {
      const response = await axios.get('/api/db_status');
      setDbStatus(response.data.data);
    } catch (err) {
      console.error('Failed to fetch DB status:', err);
    }
  };

  const fetchResumes = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/resumes');
      setResumes(response.data.data);
    } catch (err) {
      console.error('Failed to fetch resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchScores = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/scores');
      setScores(response.data.data);
    } catch (err) {
      console.error('Failed to fetch scores:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteResume = async (id) => {
    if (!confirm('⚠️ This will also delete all scores associated with this resume. Continue?')) return;
    
    try {
      await axios.delete(`/api/resumes/${id}`);
      fetchResumes();
      fetchDbStatus();
      if (onDataChange) onDataChange();
      alert('Resume and associated scores deleted successfully');
    } catch (err) {
      alert('Failed to delete resume');
    }
  };

  const deleteScore = async (id) => {
    if (!confirm('Are you sure you want to delete this score?')) return;
    
    try {
      await axios.delete(`/api/scores/${id}`);
      fetchScores();
      fetchDbStatus();
      if (onDataChange) onDataChange();
    } catch (err) {
      alert('Failed to delete score');
    }
  };

  const clearDatabase = async () => {
    if (!confirm('⚠️ WARNING: This will delete ALL data from the database. Are you sure?')) return;
    
    setLoading(true);
    try {
      await axios.post('/api/clear_database');
      setResumes([]);
      setScores([]);
      fetchDbStatus();
      if (onDataChange) onDataChange();
      alert('Database cleared successfully');
    } catch (err) {
      alert('Failed to clear database');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'resumes') fetchResumes();
    if (activeTab === 'scores') fetchScores();
  }, [activeTab]);

  return (
    <div className="space-y-6">
      <div className="border border-gray-200 rounded-lg p-6" style={{
        background: 'linear-gradient(135deg, rgba(59,130,246,0.06), rgba(139,92,246,0.06))',
        backdropFilter: 'blur(10px)'
      }}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Database Management</h2>
          <button
            onClick={fetchDbStatus}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Refresh Status
          </button>
        </div>

        {dbStatus && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className={`p-4 rounded-lg ${dbStatus.connected ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <h3 className="font-semibold text-gray-700 mb-2">Connection Status</h3>
              <p className={`text-lg font-bold ${dbStatus.connected ? 'text-green-600' : 'text-red-600'}`}>
                {dbStatus.connected ? '✓ Connected' : '✗ Disconnected'}
              </p>
              {dbStatus.database && (
                <p className="text-sm text-gray-600 mt-1">Database: {dbStatus.database}</p>
              )}
              {dbStatus.error && (
                <p className="text-sm text-red-600 mt-1">{dbStatus.error}</p>
              )}
            </div>

            {dbStatus.connected && dbStatus.collections && (
              <div className="p-4 rounded-lg bg-blue-50 border border-blue-200">
                <h3 className="font-semibold text-gray-700 mb-2">Collections</h3>
                <div className="space-y-1 text-sm">
                  <p className="text-gray-700">Resumes: <span className="font-bold">{dbStatus.collections.resumes}</span></p>
                  <p className="text-gray-700">Job Descriptions: <span className="font-bold">{dbStatus.collections.job_descriptions}</span></p>
                  <p className="text-gray-700">Scores: <span className="font-bold">{dbStatus.collections.scores}</span></p>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-2 mb-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('status')}
            className={`px-4 py-2 font-medium transition ${
              activeTab === 'status'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Status
          </button>
          <button
            onClick={() => setActiveTab('resumes')}
            className={`px-4 py-2 font-medium transition ${
              activeTab === 'resumes'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Resumes
          </button>
          <button
            onClick={() => setActiveTab('scores')}
            className={`px-4 py-2 font-medium transition ${
              activeTab === 'scores'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Scores
          </button>
        </div>

        {activeTab === 'status' && (
          <div className="space-y-4">
            <button
              onClick={clearDatabase}
              disabled={loading}
              className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
            >
              Clear All Data
            </button>
            <p className="text-sm text-gray-600">
              ⚠️ This will permanently delete all resumes, job descriptions, and scores from the database.
            </p>
          </div>
        )}

        {activeTab === 'resumes' && (
          <div>
            {loading ? (
              <p className="text-gray-600">Loading...</p>
            ) : resumes.length === 0 ? (
              <p className="text-gray-600">No resumes in database</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {resumes.map((resume) => (
                  <div key={resume._id} className="flex justify-between items-center p-3 bg-gray-50 rounded border border-gray-200">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800">{resume.name}</p>
                      <p className="text-sm text-gray-600">{resume.filename}</p>
                      <p className="text-xs text-gray-500">
                        Skills: {resume.skills?.slice(0, 5).join(', ')}
                        {resume.skills?.length > 5 && '...'}
                      </p>
                    </div>
                    <button
                      onClick={() => deleteResume(resume._id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-sm"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'scores' && (
          <div>
            {loading ? (
              <p className="text-gray-600">Loading...</p>
            ) : scores.length === 0 ? (
              <p className="text-gray-600">No scores in database</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {scores.map((score) => (
                  <div key={score._id} className="flex justify-between items-center p-3 bg-gray-50 rounded border border-gray-200">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800">{score.candidate_name}</p>
                      <p className="text-sm text-gray-600">{score.job_title}</p>
                      <div className="flex gap-2 text-xs mt-1">
                        <span className="text-gray-700">Skills: {score.skills_match}/10</span>
                        <span className="text-gray-700">Overall: {score.overall_fit}/10</span>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteScore(score._id)}
                      className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition text-sm"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
