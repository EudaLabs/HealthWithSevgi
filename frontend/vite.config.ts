import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Ensure files outside frontend/src/ (e.g. local/model-arena) resolve
    // node_modules from the frontend directory
    alias: {
      'recharts': path.resolve(__dirname, 'node_modules/recharts'),
      '@nivo/radar': path.resolve(__dirname, 'node_modules/@nivo/radar'),
      '@nivo/core': path.resolve(__dirname, 'node_modules/@nivo/core'),
      'react-plotly.js': path.resolve(__dirname, 'node_modules/react-plotly.js'),
      'plotly.js-basic-dist-min': path.resolve(__dirname, 'node_modules/plotly.js-basic-dist-min'),
      'react': path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8001'
    },
    // Allow serving files from local/ directory
    fs: {
      allow: ['.', '../local/model-arena'],
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-charts': ['recharts'],
          'vendor-query': ['@tanstack/react-query'],
        }
      }
    }
  }
})
