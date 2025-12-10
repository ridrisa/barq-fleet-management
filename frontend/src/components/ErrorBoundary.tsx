import { Component, ReactNode } from 'react'
import { Card, CardContent } from './ui/Card'
import { Button } from './ui/Button'
import { captureException } from '../lib/sentry'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  eventId?: string
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    // Capture the error in Sentry with component stack trace
    captureException(error, {
      componentStack: errorInfo.componentStack,
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <Card className="max-w-md w-full">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="text-6xl mb-4">⚠️</div>
                <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
                <p className="text-gray-600 mb-4">
                  {this.state.error?.message || 'An unexpected error occurred'}
                </p>
                <Button
                  onClick={() => {
                    this.setState({ hasError: false, error: undefined })
                    window.location.href = '/'
                  }}
                >
                  Go to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
