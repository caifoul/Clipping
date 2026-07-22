import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In docker-compose dev, API_PROXY_TARGET is set to http://api:8000 (the
// service name on the compose network); outside docker it defaults to
// localhost so `npm run dev` works standalone too.
const apiProxyTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: apiProxyTarget, changeOrigin: true },
      '/media': { target: apiProxyTarget, changeOrigin: true },
    },
  },
})
