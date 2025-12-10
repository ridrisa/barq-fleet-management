import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './index.css'
import { initPerformanceMonitoring, mark } from './utils/performanceMonitoring'
import { registerServiceWorker } from './utils/registerServiceWorker'
import { initSentry } from './lib/sentry'

// Initialize Sentry early for error tracking
initSentry()

// Mark app start for performance tracking
mark('app-init-start')

// Initialize performance monitoring
if (import.meta.env.PROD || import.meta.env.VITE_ENABLE_PERF_MONITORING === 'true') {
  initPerformanceMonitoring()
}

// Register service worker
registerServiceWorker()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

// Mark before render
mark('app-render-start')

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)

// Mark after render
mark('app-render-complete')
