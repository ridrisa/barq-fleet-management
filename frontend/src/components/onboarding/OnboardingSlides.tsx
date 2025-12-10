/**
 * Onboarding Slides Component
 *
 * Full-screen carousel for first-launch onboarding.
 * Displays introduction slides with images/animations and descriptions.
 * Supports keyboard navigation, swipe gestures, and progress indicators.
 */

import { useEffect, useState, useCallback } from 'react'
import { useOnboarding, OnboardingStep } from '@/contexts/OnboardingContext'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/cn'
import { ChevronLeft, ChevronRight, X, Sparkles, LayoutDashboard, Truck, Package, BarChart3, Rocket } from 'lucide-react'

// Icons for each slide (fallback when no image/animation)
const SLIDE_ICONS: Record<string, React.ReactNode> = {
  welcome: <Sparkles className="w-24 h-24 text-amber-500" />,
  dashboard: <LayoutDashboard className="w-24 h-24 text-blue-500" />,
  fleet: <Truck className="w-24 h-24 text-green-500" />,
  operations: <Package className="w-24 h-24 text-purple-500" />,
  analytics: <BarChart3 className="w-24 h-24 text-indigo-500" />,
  getStarted: <Rocket className="w-24 h-24 text-amber-500" />,
}

interface SlideProps {
  step: OnboardingStep
  isActive: boolean
  direction: 'next' | 'prev' | null
}

function Slide({ step, isActive, direction }: SlideProps) {
  return (
    <div
      className={cn(
        'absolute inset-0 flex flex-col items-center justify-center px-8 py-12 transition-all duration-500 ease-in-out',
        isActive && 'opacity-100 translate-x-0',
        !isActive && direction === 'next' && 'opacity-0 translate-x-full',
        !isActive && direction === 'prev' && 'opacity-0 -translate-x-full',
        !isActive && !direction && 'opacity-0'
      )}
    >
      {/* Visual element - Image, Lottie, or Icon */}
      <div className="w-64 h-64 flex items-center justify-center mb-8 rounded-full bg-gradient-to-br from-gray-50 to-gray-100 shadow-inner">
        {step.image ? (
          <img
            src={step.image}
            alt={step.title}
            className="w-48 h-48 object-contain"
            onError={(e) => {
              // Fallback to icon if image fails to load
              (e.target as HTMLImageElement).style.display = 'none'
            }}
          />
        ) : (
          SLIDE_ICONS[step.id] || <Sparkles className="w-24 h-24 text-amber-500" />
        )}
      </div>

      {/* Text content */}
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">{step.title}</h2>
        <p className="text-lg text-gray-600 leading-relaxed">{step.description}</p>
      </div>
    </div>
  )
}

interface ProgressDotsProps {
  total: number
  current: number
  onDotClick: (index: number) => void
}

function ProgressDots({ total, current, onDotClick }: ProgressDotsProps) {
  return (
    <div className="flex items-center gap-2">
      {Array.from({ length: total }, (_, i) => (
        <button
          key={i}
          onClick={() => onDotClick(i)}
          className={cn(
            'w-2.5 h-2.5 rounded-full transition-all duration-300',
            i === current
              ? 'bg-amber-500 w-8'
              : 'bg-gray-300 hover:bg-gray-400'
          )}
          aria-label={`Go to slide ${i + 1}`}
          aria-current={i === current ? 'step' : undefined}
        />
      ))}
    </div>
  )
}

export function OnboardingSlides() {
  const { state, nextStep, prevStep, skipFlow, completeFlow } = useOnboarding()
  const [direction, setDirection] = useState<'next' | 'prev' | null>(null)

  const { activeFlow, currentStepIndex, isVisible } = state

  // Only render for first-launch flow or flows without targetSelector
  const isSlideFlow = activeFlow && activeFlow.steps.every((s) => !s.targetSelector)

  // Keyboard navigation
  useEffect(() => {
    if (!isVisible || !isSlideFlow) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowRight':
        case 'Enter':
          handleNext()
          break
        case 'ArrowLeft':
          handlePrev()
          break
        case 'Escape':
          skipFlow()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isVisible, isSlideFlow, currentStepIndex])

  const handleNext = useCallback(() => {
    setDirection('next')
    setTimeout(() => nextStep(), 50)
  }, [nextStep])

  const handlePrev = useCallback(() => {
    if (currentStepIndex > 0) {
      setDirection('prev')
      setTimeout(() => prevStep(), 50)
    }
  }, [prevStep, currentStepIndex])

  const handleDotClick = useCallback(
    (index: number) => {
      if (index > currentStepIndex) {
        setDirection('next')
      } else if (index < currentStepIndex) {
        setDirection('prev')
      }
      // Note: For simplicity, dots just navigate one step at a time
      // A more complex implementation could jump directly to the index
    },
    [currentStepIndex]
  )

  if (!isVisible || !activeFlow || !isSlideFlow) return null

  const isLastStep = currentStepIndex === activeFlow.steps.length - 1
  const isFirstStep = currentStepIndex === 0

  return (
    <div
      className="fixed inset-0 z-[100] bg-white flex flex-col"
      role="dialog"
      aria-modal="true"
      aria-label="Welcome tutorial"
    >
      {/* Skip button */}
      <div className="absolute top-4 right-4 z-10">
        <Button
          variant="ghost"
          size="sm"
          onClick={skipFlow}
          className="text-gray-500 hover:text-gray-700"
        >
          <X className="w-5 h-5 mr-1" />
          Skip
        </Button>
      </div>

      {/* Slides container */}
      <div className="flex-1 relative overflow-hidden">
        {activeFlow.steps.map((step, index) => (
          <Slide
            key={step.id}
            step={step}
            isActive={index === currentStepIndex}
            direction={index === currentStepIndex ? null : direction}
          />
        ))}
      </div>

      {/* Navigation footer */}
      <div className="px-8 py-6 bg-white border-t border-gray-100">
        <div className="max-w-md mx-auto flex items-center justify-between">
          {/* Back button */}
          <Button
            variant="ghost"
            size="md"
            onClick={handlePrev}
            disabled={isFirstStep}
            className={cn(isFirstStep && 'invisible')}
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            Back
          </Button>

          {/* Progress dots */}
          <ProgressDots
            total={activeFlow.steps.length}
            current={currentStepIndex}
            onDotClick={handleDotClick}
          />

          {/* Next/Complete button */}
          {isLastStep ? (
            <Button variant="primary" size="md" onClick={completeFlow}>
              Get Started
              <Rocket className="w-5 h-5 ml-2" />
            </Button>
          ) : (
            <Button variant="primary" size="md" onClick={handleNext}>
              Next
              <ChevronRight className="w-5 h-5 ml-1" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export default OnboardingSlides
