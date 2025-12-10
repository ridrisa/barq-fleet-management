/**
 * Tooltip / Coach Mark Component
 *
 * A positioned tooltip that highlights specific UI elements during
 * feature tours and guided walkthroughs. Supports:
 * - Automatic positioning relative to target elements
 * - Spotlight effect to dim surrounding UI
 * - Animation on entry/exit
 * - Keyboard navigation
 */

import { useEffect, useState, useRef } from 'react'
import { useOnboarding, OnboardingStep } from '@/contexts/OnboardingContext'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/cn'
import { X, ChevronLeft, ChevronRight, Target } from 'lucide-react'
import { createPortal } from 'react-dom'

interface TooltipPosition {
  top: number
  left: number
  arrowPosition: 'top' | 'bottom' | 'left' | 'right'
}

interface TargetRect {
  top: number
  left: number
  width: number
  height: number
}

function calculatePosition(
  targetRect: TargetRect,
  tooltipWidth: number,
  tooltipHeight: number,
  preferredPosition: 'top' | 'bottom' | 'left' | 'right' | 'center'
): TooltipPosition {
  const padding = 16
  const arrowSize = 12
  const viewport = {
    width: window.innerWidth,
    height: window.innerHeight,
  }

  // Center of target
  const targetCenterX = targetRect.left + targetRect.width / 2
  const targetCenterY = targetRect.top + targetRect.height / 2

  let top: number
  let left: number
  let arrowPosition: 'top' | 'bottom' | 'left' | 'right' = 'top'

  switch (preferredPosition) {
    case 'bottom':
      top = targetRect.top + targetRect.height + padding + arrowSize
      left = targetCenterX - tooltipWidth / 2
      arrowPosition = 'top'
      break
    case 'top':
      top = targetRect.top - tooltipHeight - padding - arrowSize
      left = targetCenterX - tooltipWidth / 2
      arrowPosition = 'bottom'
      break
    case 'right':
      top = targetCenterY - tooltipHeight / 2
      left = targetRect.left + targetRect.width + padding + arrowSize
      arrowPosition = 'left'
      break
    case 'left':
      top = targetCenterY - tooltipHeight / 2
      left = targetRect.left - tooltipWidth - padding - arrowSize
      arrowPosition = 'right'
      break
    default: // center - position below by default
      top = targetRect.top + targetRect.height + padding + arrowSize
      left = targetCenterX - tooltipWidth / 2
      arrowPosition = 'top'
  }

  // Keep tooltip within viewport bounds
  if (left < padding) left = padding
  if (left + tooltipWidth > viewport.width - padding) {
    left = viewport.width - tooltipWidth - padding
  }
  if (top < padding) top = padding
  if (top + tooltipHeight > viewport.height - padding) {
    top = viewport.height - tooltipHeight - padding
  }

  return { top, left, arrowPosition }
}

interface SpotlightOverlayProps {
  targetRect: TargetRect | null
  onClick: () => void
}

function SpotlightOverlay({ targetRect, onClick }: SpotlightOverlayProps) {
  if (!targetRect) return null

  const padding = 8
  const borderRadius = 8

  return (
    <div
      className="fixed inset-0 z-[99] cursor-pointer"
      onClick={onClick}
      aria-hidden="true"
    >
      {/* Semi-transparent overlay with a "hole" for the target element */}
      <svg className="w-full h-full">
        <defs>
          <mask id="spotlight-mask">
            <rect width="100%" height="100%" fill="white" />
            <rect
              x={targetRect.left - padding}
              y={targetRect.top - padding}
              width={targetRect.width + padding * 2}
              height={targetRect.height + padding * 2}
              rx={borderRadius}
              ry={borderRadius}
              fill="black"
            />
          </mask>
        </defs>
        <rect
          width="100%"
          height="100%"
          fill="rgba(0, 0, 0, 0.6)"
          mask="url(#spotlight-mask)"
        />
      </svg>

      {/* Pulse animation around target */}
      <div
        className="absolute border-2 border-amber-500 rounded-lg animate-pulse pointer-events-none"
        style={{
          top: targetRect.top - padding,
          left: targetRect.left - padding,
          width: targetRect.width + padding * 2,
          height: targetRect.height + padding * 2,
          boxShadow: '0 0 0 4px rgba(245, 158, 11, 0.3)',
        }}
      />
    </div>
  )
}

interface TooltipContentProps {
  step: OnboardingStep
  position: TooltipPosition
  currentIndex: number
  totalSteps: number
  onNext: () => void
  onPrev: () => void
  onSkip: () => void
  onClose: () => void
}

function TooltipContent({
  step,
  position,
  currentIndex,
  totalSteps,
  onNext,
  onPrev,
  onSkip,
  onClose,
}: TooltipContentProps) {
  const tooltipRef = useRef<HTMLDivElement>(null)
  const isLastStep = currentIndex === totalSteps - 1
  const isFirstStep = currentIndex === 0

  // Arrow styles based on position
  const arrowStyles = {
    top: 'bottom-full left-1/2 -translate-x-1/2 translate-y-[1px] border-l-transparent border-r-transparent border-t-transparent border-b-white',
    bottom: 'top-full left-1/2 -translate-x-1/2 -translate-y-[1px] border-l-transparent border-r-transparent border-b-transparent border-t-white',
    left: 'right-full top-1/2 -translate-y-1/2 translate-x-[1px] border-t-transparent border-b-transparent border-l-transparent border-r-white',
    right: 'left-full top-1/2 -translate-y-1/2 -translate-x-[1px] border-t-transparent border-b-transparent border-r-transparent border-l-white',
  }

  return (
    <div
      ref={tooltipRef}
      className={cn(
        'fixed z-[100] bg-white rounded-lg shadow-xl border border-gray-200',
        'w-80 animate-in fade-in zoom-in-95 duration-200'
      )}
      style={{
        top: position.top,
        left: position.left,
      }}
      role="tooltip"
    >
      {/* Arrow */}
      <div
        className={cn(
          'absolute w-0 h-0 border-8',
          arrowStyles[position.arrowPosition]
        )}
      />

      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100 transition-colors"
        aria-label="Close tooltip"
      >
        <X className="w-4 h-4" />
      </button>

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
            <Target className="w-4 h-4 text-amber-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{step.title}</h3>
          </div>
        </div>
        <p className="text-sm text-gray-600 leading-relaxed mb-4">
          {step.description}
        </p>

        {/* Progress and navigation */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-500">
            {currentIndex + 1} of {totalSteps}
          </span>

          <div className="flex items-center gap-2">
            {!isFirstStep && (
              <Button variant="ghost" size="sm" onClick={onPrev}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
            )}
            {isLastStep ? (
              <Button variant="primary" size="sm" onClick={onSkip}>
                Done
              </Button>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onSkip}
                  className="text-gray-500"
                >
                  Skip
                </Button>
                <Button variant="primary" size="sm" onClick={onNext}>
                  Next
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export function OnboardingTooltip() {
  const { state, nextStep, prevStep, skipFlow, completeFlow, hideTooltip } = useOnboarding()
  const [targetRect, setTargetRect] = useState<TargetRect | null>(null)
  const [position, setPosition] = useState<TooltipPosition | null>(null)

  const { activeFlow, currentStepIndex, isVisible } = state

  // Only render for tooltip flows (with targetSelector)
  const isTooltipFlow = activeFlow && activeFlow.steps.some((s) => s.targetSelector)
  const currentStep = activeFlow?.steps[currentStepIndex]

  // Find and track target element position
  useEffect(() => {
    if (!isVisible || !isTooltipFlow || !currentStep?.targetSelector) {
      setTargetRect(null)
      return
    }

    const updatePosition = () => {
      const targetElement = document.querySelector(currentStep.targetSelector!)
      if (targetElement) {
        const rect = targetElement.getBoundingClientRect()
        setTargetRect({
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height,
        })
      } else {
        setTargetRect(null)
        console.warn(`Onboarding target not found: ${currentStep.targetSelector}`)
      }
    }

    updatePosition()

    // Update on scroll/resize
    window.addEventListener('scroll', updatePosition, true)
    window.addEventListener('resize', updatePosition)

    return () => {
      window.removeEventListener('scroll', updatePosition, true)
      window.removeEventListener('resize', updatePosition)
    }
  }, [isVisible, isTooltipFlow, currentStep])

  // Calculate tooltip position when target changes
  useEffect(() => {
    if (!targetRect || !currentStep) {
      setPosition(null)
      return
    }

    const tooltipWidth = 320
    const tooltipHeight = 180 // Approximate height

    const newPosition = calculatePosition(
      targetRect,
      tooltipWidth,
      tooltipHeight,
      currentStep.position || 'bottom'
    )
    setPosition(newPosition)
  }, [targetRect, currentStep])

  // Keyboard navigation
  useEffect(() => {
    if (!isVisible || !isTooltipFlow) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowRight':
        case 'Enter':
          nextStep()
          break
        case 'ArrowLeft':
          prevStep()
          break
        case 'Escape':
          skipFlow()
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isVisible, isTooltipFlow, nextStep, prevStep, skipFlow])

  if (!isVisible || !activeFlow || !isTooltipFlow || !currentStep || !position) {
    return null
  }

  const handleClose = () => {
    if (activeFlow.id === 'tooltip') {
      hideTooltip()
    } else {
      skipFlow()
    }
  }

  return createPortal(
    <>
      <SpotlightOverlay targetRect={targetRect} onClick={handleClose} />
      <TooltipContent
        step={currentStep}
        position={position}
        currentIndex={currentStepIndex}
        totalSteps={activeFlow.steps.length}
        onNext={nextStep}
        onPrev={prevStep}
        onSkip={completeFlow}
        onClose={handleClose}
      />
    </>,
    document.body
  )
}

export default OnboardingTooltip
