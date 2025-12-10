/**
 * Onboarding Context
 *
 * Manages the state and flow of in-app onboarding experiences:
 * - First-launch onboarding slides
 * - Feature tour walkthroughs
 * - Contextual tooltips and coach marks
 *
 * Persists completion status in localStorage to avoid showing
 * completed onboarding flows again.
 */

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'

// Types for different onboarding experiences
export interface OnboardingStep {
  id: string
  title: string
  description: string
  image?: string
  lottieAnimation?: string
  targetSelector?: string // CSS selector for highlight
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center'
}

export interface OnboardingFlow {
  id: string
  name: string
  steps: OnboardingStep[]
  triggerRoute?: string // Auto-trigger on specific routes
}

// Predefined onboarding flows
export const ONBOARDING_FLOWS: Record<string, OnboardingFlow> = {
  firstLaunch: {
    id: 'firstLaunch',
    name: 'Welcome to SYNC',
    steps: [
      {
        id: 'welcome',
        title: 'Welcome to SYNC Fleet Management',
        description: 'Your complete solution for managing delivery operations, fleet assets, workforce, and business analytics.',
        image: '/onboarding/welcome.svg',
        position: 'center',
      },
      {
        id: 'dashboard',
        title: 'Command Center Dashboard',
        description: 'Get real-time insights into your entire operation at a glance. Monitor KPIs, track deliveries, and manage your fleet from one place.',
        image: '/onboarding/dashboard.svg',
        position: 'center',
      },
      {
        id: 'fleet',
        title: 'Fleet Management',
        description: 'Manage your couriers and vehicles efficiently. Track assignments, monitor performance, and maintain your fleet with ease.',
        image: '/onboarding/fleet.svg',
        position: 'center',
      },
      {
        id: 'operations',
        title: 'Streamlined Operations',
        description: 'Handle deliveries, dispatch orders, and manage COD reconciliation. Auto-dispatch finds the best courier automatically.',
        image: '/onboarding/operations.svg',
        position: 'center',
      },
      {
        id: 'analytics',
        title: 'Powerful Analytics',
        description: 'Make data-driven decisions with comprehensive reports and customizable dashboards. Export reports in multiple formats.',
        image: '/onboarding/analytics.svg',
        position: 'center',
      },
      {
        id: 'getStarted',
        title: 'Ready to Get Started?',
        description: 'Explore your dashboard and discover all the features SYNC has to offer. Click the help icon anytime for assistance.',
        image: '/onboarding/start.svg',
        position: 'center',
      },
    ],
  },
  dashboardTour: {
    id: 'dashboardTour',
    name: 'Dashboard Tour',
    triggerRoute: '/dashboard',
    steps: [
      {
        id: 'kpiCards',
        title: 'Key Performance Indicators',
        description: 'These cards show your most important metrics at a glance. Hover over them for more details.',
        targetSelector: '[data-tour="kpi-cards"]',
        position: 'bottom',
      },
      {
        id: 'charts',
        title: 'Visual Analytics',
        description: 'Interactive charts show trends and patterns. Click legend items to filter data.',
        targetSelector: '[data-tour="charts"]',
        position: 'top',
      },
      {
        id: 'alerts',
        title: 'System Alerts',
        description: 'Important notifications appear here. Click any alert to take action.',
        targetSelector: '[data-tour="alerts"]',
        position: 'left',
      },
      {
        id: 'quickActions',
        title: 'Quick Actions',
        description: 'Frequently used actions are just one click away. Create deliveries, add couriers, and more.',
        targetSelector: '[data-tour="quick-actions"]',
        position: 'left',
      },
    ],
  },
  fleetTour: {
    id: 'fleetTour',
    name: 'Fleet Management Tour',
    triggerRoute: '/fleet/couriers',
    steps: [
      {
        id: 'courierList',
        title: 'Courier Directory',
        description: 'View all your delivery personnel with their status, assigned vehicles, and today\'s stats.',
        targetSelector: '[data-tour="courier-list"]',
        position: 'bottom',
      },
      {
        id: 'filters',
        title: 'Powerful Filters',
        description: 'Filter couriers by status, zone, or search by name. Find who you need instantly.',
        targetSelector: '[data-tour="filters"]',
        position: 'bottom',
      },
      {
        id: 'bulkActions',
        title: 'Bulk Operations',
        description: 'Select multiple couriers to perform bulk actions like assignment changes or notifications.',
        targetSelector: '[data-tour="bulk-actions"]',
        position: 'bottom',
      },
    ],
  },
  deliveryTour: {
    id: 'deliveryTour',
    name: 'Delivery Management Tour',
    triggerRoute: '/operations/deliveries',
    steps: [
      {
        id: 'deliveryList',
        title: 'Delivery Overview',
        description: 'All orders with their status, assigned courier, and timeline. Track every delivery in real-time.',
        targetSelector: '[data-tour="delivery-list"]',
        position: 'bottom',
      },
      {
        id: 'statusFlow',
        title: 'Order Status Flow',
        description: 'Orders move through stages: Pending → Assigned → Picked Up → In Transit → Delivered',
        targetSelector: '[data-tour="status-filter"]',
        position: 'bottom',
      },
      {
        id: 'autoDispatch',
        title: 'Auto-Dispatch',
        description: 'Let SYNC automatically assign the best courier based on location, workload, and skills.',
        targetSelector: '[data-tour="auto-dispatch"]',
        position: 'left',
      },
    ],
  },
}

// Storage key for persisting onboarding state
const ONBOARDING_STORAGE_KEY = 'sync_onboarding_completed'

interface OnboardingState {
  completedFlows: string[]
  activeFlow: OnboardingFlow | null
  currentStepIndex: number
  isVisible: boolean
}

interface OnboardingContextType {
  // State
  state: OnboardingState
  // Flow control
  startFlow: (flowId: string) => void
  nextStep: () => void
  prevStep: () => void
  skipFlow: () => void
  completeFlow: () => void
  // Check status
  isFlowCompleted: (flowId: string) => boolean
  shouldShowFlow: (flowId: string) => boolean
  // Manual trigger for tooltips
  showTooltip: (step: OnboardingStep) => void
  hideTooltip: () => void
  // Reset all onboarding (for testing or re-onboarding)
  resetOnboarding: () => void
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined)

interface OnboardingProviderProps {
  children: ReactNode
}

export function OnboardingProvider({ children }: OnboardingProviderProps) {
  const [state, setState] = useState<OnboardingState>(() => {
    // Load completed flows from localStorage
    const stored = localStorage.getItem(ONBOARDING_STORAGE_KEY)
    const completedFlows = stored ? JSON.parse(stored) : []
    return {
      completedFlows,
      activeFlow: null,
      currentStepIndex: 0,
      isVisible: false,
    }
  })

  // Persist completed flows to localStorage
  useEffect(() => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(state.completedFlows))
  }, [state.completedFlows])

  const isFlowCompleted = useCallback(
    (flowId: string) => state.completedFlows.includes(flowId),
    [state.completedFlows]
  )

  const shouldShowFlow = useCallback(
    (flowId: string) => !state.completedFlows.includes(flowId) && !state.activeFlow,
    [state.completedFlows, state.activeFlow]
  )

  const startFlow = useCallback((flowId: string) => {
    const flow = ONBOARDING_FLOWS[flowId]
    if (!flow) {
      console.warn(`Onboarding flow "${flowId}" not found`)
      return
    }
    setState((prev) => ({
      ...prev,
      activeFlow: flow,
      currentStepIndex: 0,
      isVisible: true,
    }))
  }, [])

  const nextStep = useCallback(() => {
    setState((prev) => {
      if (!prev.activeFlow) return prev
      const nextIndex = prev.currentStepIndex + 1
      if (nextIndex >= prev.activeFlow.steps.length) {
        // Flow complete
        return {
          ...prev,
          completedFlows: [...prev.completedFlows, prev.activeFlow.id],
          activeFlow: null,
          currentStepIndex: 0,
          isVisible: false,
        }
      }
      return {
        ...prev,
        currentStepIndex: nextIndex,
      }
    })
  }, [])

  const prevStep = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentStepIndex: Math.max(0, prev.currentStepIndex - 1),
    }))
  }, [])

  const skipFlow = useCallback(() => {
    setState((prev) => {
      if (!prev.activeFlow) return prev
      return {
        ...prev,
        completedFlows: [...prev.completedFlows, prev.activeFlow.id],
        activeFlow: null,
        currentStepIndex: 0,
        isVisible: false,
      }
    })
  }, [])

  const completeFlow = useCallback(() => {
    setState((prev) => {
      if (!prev.activeFlow) return prev
      return {
        ...prev,
        completedFlows: [...prev.completedFlows, prev.activeFlow.id],
        activeFlow: null,
        currentStepIndex: 0,
        isVisible: false,
      }
    })
  }, [])

  const showTooltip = useCallback((step: OnboardingStep) => {
    setState((prev) => ({
      ...prev,
      activeFlow: {
        id: 'tooltip',
        name: 'Tooltip',
        steps: [step],
      },
      currentStepIndex: 0,
      isVisible: true,
    }))
  }, [])

  const hideTooltip = useCallback(() => {
    setState((prev) => ({
      ...prev,
      activeFlow: null,
      currentStepIndex: 0,
      isVisible: false,
    }))
  }, [])

  const resetOnboarding = useCallback(() => {
    localStorage.removeItem(ONBOARDING_STORAGE_KEY)
    setState({
      completedFlows: [],
      activeFlow: null,
      currentStepIndex: 0,
      isVisible: false,
    })
  }, [])

  const value: OnboardingContextType = {
    state,
    startFlow,
    nextStep,
    prevStep,
    skipFlow,
    completeFlow,
    isFlowCompleted,
    shouldShowFlow,
    showTooltip,
    hideTooltip,
    resetOnboarding,
  }

  return <OnboardingContext.Provider value={value}>{children}</OnboardingContext.Provider>
}

/**
 * Hook to access onboarding functionality
 *
 * @example
 * ```tsx
 * const { startFlow, shouldShowFlow } = useOnboarding()
 *
 * useEffect(() => {
 *   if (shouldShowFlow('dashboardTour')) {
 *     startFlow('dashboardTour')
 *   }
 * }, [])
 * ```
 */
export function useOnboarding(): OnboardingContextType {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error('useOnboarding must be used within an OnboardingProvider')
  }
  return context
}

export default OnboardingContext
