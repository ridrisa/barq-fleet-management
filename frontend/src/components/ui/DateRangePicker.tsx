import { forwardRef, useState } from 'react'
import { DayPicker, DateRange } from 'react-day-picker'
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns'
import { cn } from '@/lib/cn'
import 'react-day-picker/dist/style.css'

export interface DateRangePickerProps {
  // New interface (preferred)
  value?: DateRange
  onChange?: (range: DateRange | undefined) => void
  // Legacy interface support
  startDate?: string
  endDate?: string
  onRangeChange?: (startDate: string, endDate: string) => void
  // Common props
  className?: string
  disabled?: boolean
  placeholder?: string
}

type PresetRange = {
  label: string
  range: DateRange
}

export const DateRangePicker = forwardRef<HTMLDivElement, DateRangePickerProps>(
  (
    {
      value,
      onChange,
      startDate,
      endDate,
      onRangeChange,
      className,
      disabled = false,
      placeholder = 'Select date range',
    },
    ref
  ) => {
    const [isOpen, setIsOpen] = useState(false)

    // Support both new and legacy interfaces
    const initialRange: DateRange | undefined = value || (startDate && endDate ? {
      from: new Date(startDate),
      to: new Date(endDate)
    } : undefined)

    const [selectedRange, setSelectedRange] = useState<DateRange | undefined>(initialRange)

    const today = new Date()

    const presetRanges: PresetRange[] = [
      {
        label: 'Today',
        range: { from: today, to: today },
      },
      {
        label: 'Last 7 days',
        range: { from: subDays(today, 6), to: today },
      },
      {
        label: 'Last 30 days',
        range: { from: subDays(today, 29), to: today },
      },
      {
        label: 'This Month',
        range: { from: startOfMonth(today), to: endOfMonth(today) },
      },
    ]

    const handleSelect = (range: DateRange | undefined) => {
      setSelectedRange(range)

      // Call the appropriate onChange handler
      if (onChange) {
        onChange(range)
      }
      if (onRangeChange && range?.from && range?.to) {
        onRangeChange(
          format(range.from, 'yyyy-MM-dd'),
          format(range.to, 'yyyy-MM-dd')
        )
      }

      // Close if both dates are selected
      if (range?.from && range?.to) {
        setIsOpen(false)
      }
    }

    const handlePresetClick = (preset: PresetRange) => {
      setSelectedRange(preset.range)

      // Call the appropriate onChange handler
      if (onChange) {
        onChange(preset.range)
      }
      if (onRangeChange && preset.range.from && preset.range.to) {
        onRangeChange(
          format(preset.range.from, 'yyyy-MM-dd'),
          format(preset.range.to, 'yyyy-MM-dd')
        )
      }
      setIsOpen(false)
    }

    const formatRange = (range: DateRange | undefined): string => {
      if (!range?.from) return placeholder

      if (!range.to) {
        return format(range.from, 'MMM dd, yyyy')
      }

      return `${format(range.from, 'MMM dd, yyyy')} - ${format(range.to, 'MMM dd, yyyy')}`
    }

    return (
      <div ref={ref} className={cn('relative', className)}>
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={cn(
            'w-full px-4 py-2 text-left bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'flex items-center justify-between gap-2'
          )}
          aria-label="Select date range"
          aria-haspopup="dialog"
          aria-expanded={isOpen}
        >
          <span className={cn(
            'text-sm',
            !selectedRange?.from && 'text-gray-500 dark:text-gray-400',
            selectedRange?.from && 'text-gray-900 dark:text-gray-100'
          )}>
            {formatRange(selectedRange)}
          </span>
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </button>

        {isOpen && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsOpen(false)}
              aria-hidden="true"
            />
            <div
              className={cn(
                'absolute z-50 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
                'rounded-lg shadow-lg p-4 min-w-max'
              )}
              role="dialog"
              aria-label="Date range picker"
            >
              <div className="flex gap-4">
                {/* Preset Ranges */}
                <div className="space-y-1 pr-4 border-r border-gray-200 dark:border-gray-700">
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2">
                    Quick Select
                  </p>
                  {presetRanges.map((preset) => (
                    <button
                      key={preset.label}
                      type="button"
                      onClick={() => handlePresetClick(preset)}
                      className={cn(
                        'block w-full text-left px-3 py-2 text-sm rounded-md transition-colors',
                        'hover:bg-gray-100 dark:hover:bg-gray-700',
                        'focus:outline-none focus:ring-2 focus:ring-blue-500'
                      )}
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>

                {/* Calendar */}
                <div className="date-range-picker">
                  <DayPicker
                    mode="range"
                    selected={selectedRange}
                    onSelect={handleSelect}
                    numberOfMonths={2}
                    className="text-sm"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedRange(undefined)
                    if (onChange) {
                      onChange(undefined)
                    }
                    if (onRangeChange) {
                      onRangeChange('', '')
                    }
                  }}
                  className={cn(
                    'px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300',
                    'hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md',
                    'focus:outline-none focus:ring-2 focus:ring-blue-500'
                  )}
                >
                  Clear
                </button>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'px-3 py-1.5 text-sm font-medium text-white bg-blue-600',
                    'hover:bg-blue-700 rounded-md',
                    'focus:outline-none focus:ring-2 focus:ring-blue-500'
                  )}
                >
                  Done
                </button>
              </div>
            </div>
          </>
        )}

        <style>{`
          .date-range-picker .rdp {
            --rdp-cell-size: 36px;
            --rdp-accent-color: #3b82f6;
            --rdp-background-color: #dbeafe;
          }

          .date-range-picker .rdp-months {
            display: flex;
            gap: 1rem;
          }

          .date-range-picker .rdp-caption {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0.5rem;
          }

          .date-range-picker .rdp-head_cell {
            font-weight: 600;
            font-size: 0.75rem;
            color: #6b7280;
            text-transform: uppercase;
          }

          .date-range-picker .rdp-cell {
            padding: 0;
          }

          .date-range-picker .rdp-button {
            border-radius: 0.375rem;
          }

          .date-range-picker .rdp-day_selected {
            background-color: var(--rdp-accent-color);
            color: white;
          }

          .date-range-picker .rdp-day_range_middle {
            background-color: var(--rdp-background-color);
          }
        `}</style>
      </div>
    )
  }
)

DateRangePicker.displayName = 'DateRangePicker'
