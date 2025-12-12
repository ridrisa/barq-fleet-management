import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuthStore } from '@/stores/authStore'
import { loginSchema, LoginFormData } from '@/schemas'

// Google OAuth Client ID from environment
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

// Debug logging in development
if (import.meta.env.DEV) {
  console.log('Google Client ID configured:', !!GOOGLE_CLIENT_ID)
}

export default function Login() {
  const [googleLoading, setGoogleLoading] = useState(false)
  const [googleError, setGoogleError] = useState<string | null>(null)
  const { login, loginWithGoogle, isAuthenticated, isLoading, error, clearError } = useAuthStore()
  const navigate = useNavigate()
  const googleInitialized = useRef(false)
  const loginWithGoogleRef = useRef(loginWithGoogle)

  // Keep ref updated
  useEffect(() => {
    loginWithGoogleRef.current = loginWithGoogle
  }, [loginWithGoogle])

  // React Hook Form with Zod validation
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
    mode: 'onBlur',
  })

  // Initialize Google Sign-In
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) {
      console.warn('Google OAuth: VITE_GOOGLE_CLIENT_ID not configured')
      return
    }

    // Prevent multiple initializations
    if (googleInitialized.current) return

    // Check if script already loaded
    const existingScript = document.querySelector('script[src="https://accounts.google.com/gsi/client"]')

    const initializeGoogle = () => {
      if (window.google && !googleInitialized.current) {
        googleInitialized.current = true
        try {
          window.google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: async (response: { credential: string }) => {
              setGoogleLoading(true)
              setGoogleError(null)
              try {
                await loginWithGoogleRef.current(response.credential)
              } catch (err: any) {
                console.error('Google login error:', err)
                setGoogleError(err.response?.data?.detail || 'Google login failed')
              } finally {
                setGoogleLoading(false)
              }
            },
            ux_mode: 'popup',
          })

          const buttonContainer = document.getElementById('google-signin-button')
          if (buttonContainer) {
            window.google.accounts.id.renderButton(
              buttonContainer,
              {
                theme: 'outline',
                size: 'large',
                width: 320,
                text: 'signin_with',
                shape: 'rectangular',
              }
            )
            console.log('Google Sign-In button rendered successfully')
          } else {
            console.error('Google Sign-In button container not found')
          }
        } catch (err) {
          console.error('Failed to initialize Google Sign-In:', err)
          setGoogleError('Failed to load Google Sign-In')
        }
      }
    }

    if (existingScript && window.google) {
      initializeGoogle()
    } else if (!existingScript) {
      // Load Google Identity Services script
      const script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.onload = initializeGoogle
      script.onerror = () => {
        console.error('Failed to load Google Identity Services script')
        setGoogleError('Failed to load Google Sign-In')
      }
      document.head.appendChild(script)
    }

    // No cleanup - let the script persist
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    return () => clearError()
  }, [clearError])

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.email, data.password)
    } catch (err) {
      // Error is handled by the store
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="flex flex-col items-center">
          <img
            src="/images/logo.png"
            alt="SYNC Fleet"
            className="h-20 w-auto mb-4"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            SYNC Fleet Management
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                {...register('email')}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-amber-500 focus:border-amber-500 focus:z-10 sm:text-sm`}
                placeholder="Email address"
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register('password')}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-amber-500 focus:border-amber-500 focus:z-10 sm:text-sm`}
                placeholder="Password"
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading || googleLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-amber-500 hover:bg-amber-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          {/* Divider */}
          {GOOGLE_CLIENT_ID && (
            <>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-gray-50 text-gray-500">Or continue with</span>
                </div>
              </div>

              {/* Google Sign-In Button */}
              <div className="mt-4">
                <div
                  id="google-signin-button"
                  className="flex justify-center"
                  style={{ minHeight: '44px' }}
                />
                {googleLoading && (
                  <div className="mt-2 text-center text-sm text-gray-500">
                    Signing in with Google...
                  </div>
                )}
                {googleError && (
                  <div className="mt-2 text-center text-sm text-red-500">
                    {googleError}
                  </div>
                )}
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  )
}

// Add Google type declaration
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: { credential: string }) => void }) => void
          renderButton: (element: HTMLElement | null, options: Record<string, unknown>) => void
        }
      }
    }
  }
}
