import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/static/',           // assets ficam em /static/assets/...
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/api':      { target: 'http://localhost:8000', changeOrigin: true },
      '/login':    { target: 'http://localhost:8000', changeOrigin: true },
      '/logout':   { target: 'http://localhost:8000', changeOrigin: true },
      '/health':   { target: 'http://localhost:8000', changeOrigin: true },
      '/static':   { target: 'http://localhost:8000', changeOrigin: true },
      '/uploads':  { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
