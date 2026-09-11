import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  publicDir: '../public',
  server: {
    port: 5173,
    allowedHosts: ['northstar-ai-support.onrender.com'],
  },
  preview: {
    allowedHosts: ['northstar-ai-support.onrender.com'],
  },
})
