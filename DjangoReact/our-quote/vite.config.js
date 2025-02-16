import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '~bootstrap': 'node_modules/bootstrap',
    }
  },
  plugins: [react()],
})