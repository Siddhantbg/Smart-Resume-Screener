import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/score': 'http://localhost:8000',
      '/score_files': 'http://localhost:8000',
      '/parse_resume': 'http://localhost:8000',
      '/parse_jd': 'http://localhost:8000'
    }
  }
})
