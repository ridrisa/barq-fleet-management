import { ReactNode, useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/cn'
import { X, SlidersHorizontal, RotateCcw } from 'lucide-react'
import { Button } from './Button'
import { useLockBodyScroll, useSwipe, useMobile } from '@/hooks/useMobile'

export interface FilterSheetProps {
  isOpen: boolean
  onClose: () => void
  onApply?: () => void
  onClear?: () => void
  title?: string
  children: ReactNode
  // Number of active filters to display in badge
  activeFiltersCount?: number
  applyLabel?: string
  clearLabel?: string
  showApplyButton?: boolean
  showClearButton?: boolean
}

export const FilterSheet = ({
  isOpen,
  onClose,
  onApply,
  onClear,
  title = 'Filters',
  children,
  activeFiltersCount = 0,
  applyLabel = 'Apply Filters',
  clearLabel = 'Clear All',
  showApplyButton = true,
  showClearButton = true,
}: FilterSheetProps) => {
  const sheetRef = useRef<HTMLDivElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState(0)
  const startY = useRef(0)

  useLockBodyScroll(isOpen)

  // Swipe to close
  const { onTouchStart: swipeTouchStart, onTouchEnd: swipeTouchEnd } = useSwipe(
    undefined,
    undefined,
    undefined,
    onClose,
    100
  )

  // Enhanced drag handling for smooth dismiss
  const handleTouchStart = (e: React.TouchEvent) => {
    startY.current = e.touches[0].clientY
    setIsDragging(true)
    swipeTouchStart(e.nativeEvent)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging) return
    const currentY = e.touches[0].clientY
    const offset = Math.max(0, currentY - startY.current)
    setDragOffset(offset)
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    setIsDragging(false)
    if (dragOffset > 150) {
      onClose()
    }
    setDragOffset(0)
    swipeTouchEnd(e.nativeEvent)
  }

  // Focus trap
  useEffect(() => {
    if (!isOpen || !sheetRef.current) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  const handleApply = () => {
    onApply?.()
    onClose()
  }

  const handleClear = () => {
    onClear?.()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 animate-in fade-in duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Bottom Sheet */}
      <div
        ref={sheetRef}
        className={cn(
          'relative bg-white rounded-t-2xl shadow-xl w-full',
          'max-h-[85vh] flex flex-col',
          'animate-in slide-in-from-bottom duration-300',
          'pb-[env(safe-area-inset-bottom)]'
        )}
        style={{
          transform: dragOffset > 0 ? `translateY(${dragOffset}px)` : undefined,
          transition: isDragging ? 'none' : 'transform 0.3s ease-out',
        }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="filter-sheet-title"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Drag Handle */}
        <div className="flex justify-center pt-3 pb-2 cursor-grab active:cursor-grabbing">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-5 w-5 text-gray-500" />
            <h2 id="filter-sheet-title" className="text-lg font-semibold text-gray-900">
              {title}
            </h2>
            {activeFiltersCount > 0 && (
              <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                {activeFiltersCount}
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className={cn(
              'min-w-[44px] min-h-[44px] flex items-center justify-center -mr-2',
              'text-gray-400 hover:text-gray-600 transition-colors'
            )}
            aria-label="Close filters"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {children}
        </div>

        {/* Footer Actions */}
        {(showApplyButton || showClearButton) && (
          <div className="border-t border-gray-200 px-4 py-4 bg-gray-50">
            <div className="flex gap-3">
              {showClearButton && (
                <Button
                  variant="outline"
                  onClick={handleClear}
                  className="flex-1 min-h-[48px]"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  {clearLabel}
                </Button>
              )}
              {showApplyButton && (
                <Button
                  variant="primary"
                  onClick={handleApply}
                  className="flex-1 min-h-[48px]"
                >
                  {applyLabel}
                  {activeFiltersCount > 0 && (
                    <span className="ml-2 px-1.5 py-0.5 text-xs bg-white/20 rounded">
                      {activeFiltersCount}
                    </span>
                  )}
                </Button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Filter Group component for organizing filters
export interface FilterGroupProps {
  label: string
  children: ReactNode
  collapsible?: boolean
  defaultExpanded?: boolean
}

export const FilterGroup = ({
  label,
  children,
  collapsible = false,
  defaultExpanded = true,
}: FilterGroupProps) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className="mb-6 last:mb-0">
      <button
        type="button"
        className={cn(
          'flex items-center justify-between w-full text-left mb-3',
          collapsible && 'cursor-pointer'
        )}
        onClick={() => collapsible && setIsExpanded(!isExpanded)}
        disabled={!collapsible}
      >
        <span className="text-sm font-medium text-gray-700">{label}</span>
        {collapsible && (
          <svg
            className={cn(
              'h-4 w-4 text-gray-400 transition-transform',
              isExpanded && 'rotate-180'
            )}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </button>
      {(!collapsible || isExpanded) && (
        <div className="space-y-3">{children}</div>
      )}
    </div>
  )
}

// Filter Chip for quick filter selection
export interface FilterChipProps {
  label: string
  isSelected: boolean
  onChange: (selected: boolean) => void
  count?: number
}

export const FilterChip = ({
  label,
  isSelected,
  onChange,
  count,
}: FilterChipProps) => {
  return (
    <button
      type="button"
      onClick={() => onChange(!isSelected)}
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-2 rounded-full text-sm font-medium',
        'min-h-[44px] transition-colors',
        isSelected
          ? 'bg-blue-100 text-blue-700 border-2 border-blue-500'
          : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
      )}
    >
      {label}
      {count !== undefined && (
        <span
          className={cn(
            'text-xs px-1.5 py-0.5 rounded-full',
            isSelected ? 'bg-blue-200 text-blue-800' : 'bg-gray-200 text-gray-600'
          )}
        >
          {count}
        </span>
      )}
    </button>
  )
}

// Filter Trigger Button (for showing filter button that opens the sheet)
export interface FilterTriggerProps {
  onClick: () => void
  activeCount?: number
  label?: string
  className?: string
}

export const FilterTrigger = ({
  onClick,
  activeCount = 0,
  label = 'Filters',
  className,
}: FilterTriggerProps) => {
  const isMobile = useMobile('md')

  return (
    <button
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-2 px-4 py-2 rounded-lg',
        'bg-white border border-gray-300 text-gray-700',
        'hover:bg-gray-50 active:bg-gray-100 transition-colors',
        'min-h-[44px] font-medium',
        className
      )}
    >
      <SlidersHorizontal className="h-5 w-5" />
      {!isMobile && <span>{label}</span>}
      {activeCount > 0 && (
        <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-blue-600 text-white rounded-full">
          {activeCount}
        </span>
      )}
    </button>
  )
}
