import axios from 'axios';

// Get the API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create an axios instance with the base URL
const api = axios.create({
  baseURL: API_BASE_URL,
});

export default api;

// Export the base URL for other uses
export { API_BASE_URL };