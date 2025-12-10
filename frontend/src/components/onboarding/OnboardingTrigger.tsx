/**
 * Onboarding Trigger Component
 *
 * A floating help button and menu that allows users to:
 * - Restart the welcome tour
 * - Start feature-specific tours
 * - Access help resources
 *
 * Also handles automatic tour triggering based on route.
 */

import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useOnboarding, ONBOARDING_FLOWS } from '@/contexts/OnboardingContext'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/cn'
import {
  HelpCircle,
  X,
  PlayCircle,
  RotateCcw,
  LayoutDashboard,
  Truck,
  Package,
  BookOpen,
  MessageCircle,
} from 'lucide-react'

interface TourOption {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  route?: string
}

const TOUR_OPTIONS: TourOption[] = [
  {
    id: 'firstLaunch',
    name: 'Welcome Tour',
    description: 'Introduction to SYNC Fleet Management',
    icon: <PlayCircle className="w-5 h-5" />,
  },
  {
    id: 'dashboardTour',
    name: 'Dashboard Tour',
    description: 'Learn about your command center',
    icon: <LayoutDashboard className="w-5 h-5" />,
    route: '/dashboard',
  },
  {
    id: 'fleetTour',
    name: 'Fleet Tour',
    description: 'Manage couriers and vehicles',
    icon: <Truck className="w-5 h-5" />,
    route: '/fleet/couriers',
  },
  {
    id: 'deliveryTour',
    name: 'Delivery Tour',
    description: 'Handle orders and dispatch',
    icon: <Package className="w-5 h-5" />,
    route: '/operations/deliveries',
  },
]

interface OnboardingMenuProps {
  isOpen: boolean
  onClose: () => void
  onStartTour: (tourId: string) => void
  completedTours: string[]
}

function OnboardingMenu({ isOpen, onClose, onStartTour, completedTours }: OnboardingMenuProps) {
  if (!isOpen) return null

  return (
    <div
      className={cn(
        'absolute bottom-full right-0 mb-4 w-80',
        'bg-white rounded-xl shadow-xl border border-gray-200',
        'animate-in fade-in slide-in-from-bottom-4 duration-200'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-amber-500" />
          <span className="font-semibold text-gray-900">Learning Center</span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100"
          aria-label="Close menu"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Tours list */}
      <div className="py-2">
        {TOUR_OPTIONS.map((tour) => {
          const isCompleted = completedTours.includes(tour.id)

          return (
            <button
              key={tour.id}
              onClick={() => onStartTour(tour.id)}
              className={cn(
                'w-full flex items-start gap-3 px-4 py-3',
                'hover:bg-gray-50 transition-colors text-left'
              )}
            >
              <div
                className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0',
                  isCompleted ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'
                )}
              >
                {isCompleted ? (
                  <RotateCcw className="w-5 h-5" />
                ) : (
                  tour.icon
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900 text-sm">{tour.name}</span>
                  {isCompleted && (
                    <span className="text-xs text-green-600 bg-green-100 px-1.5 py-0.5 rounded">
                      Completed
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{tour.description}</p>
              </div>
            </button>
          )
        })}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 rounded-b-xl border-t border-gray-100">
        <a
          href="https://docs.syncfleet.com"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-sm text-amber-600 hover:text-amber-700"
        >
          <BookOpen className="w-4 h-4" />
          <span>View Documentation</span>
        </a>
        <a
          href="mailto:support@syncfleet.com"
          className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-700 mt-2"
        >
          <MessageCircle className="w-4 h-4" />
          <span>Contact Support</span>
        </a>
      </div>
    </div>
  )
}

export function OnboardingTrigger() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()
  const { startFlow, shouldShowFlow, isFlowCompleted, state } = useOnboarding()

  // Auto-trigger tours based on route (only once)
  useEffect(() => {
    Object.values(ONBOARDING_FLOWS).forEach((flow) => {
      if (
        flow.triggerRoute &&
        location.pathname === flow.triggerRoute &&
        shouldShowFlow(flow.id)
      ) {
        // Delay to let the page render first
        const timer = setTimeout(() => {
          startFlow(flow.id)
        }, 1000)
        return () => clearTimeout(timer)
      }
    })
  }, [location.pathname, shouldShowFlow, startFlow])

  // Check if first launch and show welcome tour
  useEffect(() => {
    if (shouldShowFlow('firstLaunch') && location.pathname !== '/login' && location.pathname !== '/landing') {
      // Small delay to let the app load
      const timer = setTimeout(() => {
        startFlow('firstLaunch')
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [shouldShowFlow, startFlow, location.pathname])

  const handleStartTour = (tourId: string) => {
    setIsMenuOpen(false)
    startFlow(tourId)
  }

  // Don't show on login/landing pages
  if (location.pathname === '/login' || location.pathname === '/landing') {
    return null
  }

  // Don't show when a tour is active
  if (state.isVisible) {
    return null
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Menu */}
      <OnboardingMenu
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        onStartTour={handleStartTour}
        completedTours={state.completedFlows}
      />

      {/* Floating button */}
      <Button
        variant="primary"
        size="lg"
        onClick={() => setIsMenuOpen(!isMenuOpen)}
        className={cn(
          'rounded-full w-14 h-14 p-0 shadow-lg',
          'hover:scale-105 transition-transform',
          isMenuOpen && 'bg-gray-700'
        )}
        aria-label={isMenuOpen ? 'Close help menu' : 'Open help menu'}
        aria-expanded={isMenuOpen}
      >
        {isMenuOpen ? (
          <X className="w-6 h-6" />
        ) : (
          <HelpCircle className="w-6 h-6" />
        )}
      </Button>

      {/* Pulse indicator for new users */}
      {!isFlowCompleted('firstLaunch') && !isMenuOpen && (
        <span className="absolute -top-1 -right-1 flex h-4 w-4">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-4 w-4 bg-amber-500" />
        </span>
      )}
    </div>
  )
}

export default OnboardingTrigger
