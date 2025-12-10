/**
 * Onboarding Components
 *
 * Export all onboarding-related components for easy imports.
 */

export { OnboardingSlides } from './OnboardingSlides'
export { OnboardingTooltip } from './Tooltip'
export { OnboardingTrigger } from './OnboardingTrigger'

// Re-export context and hooks
export {
  OnboardingProvider,
  useOnboarding,
  ONBOARDING_FLOWS,
  type OnboardingStep,
  type OnboardingFlow,
} from '@/contexts/OnboardingContext'
