import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'
import { sentryVitePlugin } from '@sentry/vite-plugin'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = mode === 'production'
  const isAnalyze = process.env.ANALYZE === 'true'

  return {
    plugins: [
      react(),
      // Gzip compression
      isProduction && viteCompression({
        verbose: true,
        disable: false,
        threshold: 10240, // Only compress files larger than 10KB
        algorithm: 'gzip',
        ext: '.gz',
      }),
      // Brotli compression (better compression ratio)
      isProduction && viteCompression({
        verbose: true,
        disable: false,
        threshold: 10240,
        algorithm: 'brotliCompress',
        ext: '.br',
      }),
      // Bundle analyzer
      isAnalyze && visualizer({
        open: true,
        filename: 'dist/stats.html',
        gzipSize: true,
        brotliSize: true,
      }),
      // Sentry source maps upload (production only)
      isProduction && env.SENTRY_AUTH_TOKEN && sentryVitePlugin({
        org: 'barqapp-o3',
        project: 'barq-fleet-frontend',
        authToken: env.SENTRY_AUTH_TOKEN,
        telemetry: false,
      }),
    ].filter(Boolean),

    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },

    server: {
      port: 3002,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },

    build: {
      // Target modern browsers for better optimization
      target: 'es2015',

      // Source maps for production (required for Sentry error tracking)
      sourcemap: true,

      // Minification
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: isProduction, // Remove console.logs in production
          drop_debugger: true,
        },
      },

      // Chunk size warnings
      chunkSizeWarningLimit: 1000,

      // Rollup options for code splitting
      rollupOptions: {
        output: {
          // Manual chunk splitting strategy
          manualChunks: {
            // Core React dependencies
            'vendor-react': [
              'react',
              'react-dom',
              'react-router-dom',
            ],

            // UI Components
            'vendor-ui': [
              'lucide-react',
              'react-hot-toast',
              'react-day-picker',
              'react-dropzone',
            ],

            // Forms and validation
            'vendor-forms': [
              'react-hook-form',
              '@hookform/resolvers',
              'zod',
            ],

            // Charts (heavy library - separate chunk)
            'vendor-charts': [
              'recharts',
            ],

            // Data fetching and state
            'vendor-data': [
              '@tanstack/react-query',
              'axios',
              'zustand',
            ],

            // Utilities
            'vendor-utils': [
              'date-fns',
              'clsx',
              'tailwind-merge',
              'class-variance-authority',
            ],

            // Internationalization
            'vendor-i18n': [
              'i18next',
              'react-i18next',
              'i18next-browser-languagedetector',
              'i18next-http-backend',
            ],

            // Document generation (heavy - separate chunk)
            'vendor-documents': [
              'jspdf',
              'html2canvas',
              'xlsx',
            ],
          },

          // Asset file naming
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name?.split('.');
            let extType = info?.[info.length - 1];

            if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name || '')) {
              extType = 'images';
            } else if (/\.(woff|woff2|eot|ttf|otf)$/i.test(assetInfo.name || '')) {
              extType = 'fonts';
            } else if (/\.css$/i.test(assetInfo.name || '')) {
              return 'assets/css/[name]-[hash][extname]';
            }

            return `assets/${extType}/[name]-[hash][extname]`;
          },

          // Chunk file naming
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
        },
      },

      // Optimize dependencies
      commonjsOptions: {
        include: [/node_modules/],
        transformMixedEsModules: true,
      },
    },

    // Optimize dependencies
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@tanstack/react-query',
        'axios',
        'zustand',
        'date-fns',
        'recharts',
        'es-toolkit',
        'es-toolkit/compat',
      ],
      exclude: [
        // Exclude heavy libraries from pre-bundling (load on demand)
        'jspdf',
        'html2canvas',
        'xlsx',
      ],
    },

    // Performance hints
    preview: {
      port: 3000,
    },
  }
})
