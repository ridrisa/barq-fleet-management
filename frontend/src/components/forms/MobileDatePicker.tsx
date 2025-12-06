import { useState, forwardRef, useMemo } from 'react'
import { cn } from '@/lib/cn'
import { Calendar, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { useMobile, useLockBodyScroll } from '@/hooks/useMobile'
import { Button } from '@/components/ui/Button'

export interface MobileDatePickerProps {
  value?: string
  onChange?: (date: string) => void
  label?: string
  error?: string
  helperText?: string
  placeholder?: string
  disabled?: boolean
  minDate?: string
  maxDate?: string
  className?: string
}

// Calendar helper functions
const getDaysInMonth = (year: number, month: number) => {
  return new Date(year, month + 1, 0).getDate()
}

const getFirstDayOfMonth = (year: number, month: number) => {
  return new Date(year, month, 1).getDay()
}

const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0]
}

const parseDate = (dateString: string) => {
  const [year, month, day] = dateString.split('-').map(Number)
  return new Date(year, month - 1, day)
}

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export const MobileDatePicker = forwardRef<HTMLInputElement, MobileDatePickerProps>(
  (
    {
      value,
      onChange,
      label,
      error,
      helperText,
      placeholder = 'Select date',
      disabled = false,
      minDate,
      maxDate,
      className,
    },
    ref
  ) => {
    const isMobile = useMobile('sm')
    const [isOpen, setIsOpen] = useState(false)

    // Calendar state
    const today = new Date()
    const initialDate = value ? parseDate(value) : today
    const [viewYear, setViewYear] = useState(initialDate.getFullYear())
    const [viewMonth, setViewMonth] = useState(initialDate.getMonth())
    const [selectedDate, setSelectedDate] = useState<Date | null>(
      value ? parseDate(value) : null
    )

    useLockBodyScroll(isOpen && isMobile)

    // Generate calendar days
    const calendarDays = useMemo(() => {
      const daysInMonth = getDaysInMonth(viewYear, viewMonth)
      const firstDay = getFirstDayOfMonth(viewYear, viewMonth)
      const days: (number | null)[] = []

      // Add empty slots for days before the first day of the month
      for (let i = 0; i < firstDay; i++) {
        days.push(null)
      }

      // Add days of the month
      for (let i = 1; i <= daysInMonth; i++) {
        days.push(i)
      }

      return days
    }, [viewYear, viewMonth])

    const handlePrevMonth = () => {
      if (viewMonth === 0) {
        setViewMonth(11)
        setViewYear(viewYear - 1)
      } else {
        setViewMonth(viewMonth - 1)
      }
    }

    const handleNextMonth = () => {
      if (viewMonth === 11) {
        setViewMonth(0)
        setViewYear(viewYear + 1)
      } else {
        setViewMonth(viewMonth + 1)
      }
    }

    const handleDateSelect = (day: number) => {
      const newDate = new Date(viewYear, viewMonth, day)
      setSelectedDate(newDate)
    }

    const handleConfirm = () => {
      if (selectedDate) {
        onChange?.(formatDate(selectedDate))
      }
      setIsOpen(false)
    }

    const handleClear = () => {
      setSelectedDate(null)
      onChange?.('')
      setIsOpen(false)
    }

    const isDateDisabled = (day: number) => {
      const date = new Date(viewYear, viewMonth, day)
      if (minDate && date < parseDate(minDate)) return true
      if (maxDate && date > parseDate(maxDate)) return true
      return false
    }

    const isToday = (day: number) => {
      return (
        viewYear === today.getFullYear() &&
        viewMonth === today.getMonth() &&
        day === today.getDate()
      )
    }

    const isSelected = (day: number) => {
      if (!selectedDate) return false
      return (
        viewYear === selectedDate.getFullYear() &&
        viewMonth === selectedDate.getMonth() &&
        day === selectedDate.getDate()
      )
    }

    const displayValue = value
      ? new Date(value).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        })
      : ''

    // For desktop, use native date input
    if (!isMobile) {
      return (
        <div className={cn('w-full', className)}>
          {label && (
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {label}
            </label>
          )}
          <div className="relative">
            <input
              ref={ref}
              type="date"
              value={value || ''}
              onChange={(e) => onChange?.(e.target.value)}
              disabled={disabled}
              min={minDate}
              max={maxDate}
              className={cn(
                'block w-full rounded-lg border border-gray-300 px-4 py-2 pr-10 text-gray-900',
                'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'disabled:bg-gray-100 disabled:cursor-not-allowed',
                error && 'border-red-500 focus:ring-red-500'
              )}
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <Calendar className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          {helperText && !error && (
            <p className="mt-1 text-sm text-gray-500">{helperText}</p>
          )}
        </div>
      )
    }

    // Mobile: Custom bottom sheet calendar
    return (
      <div className={cn('w-full', className)}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}

        {/* Trigger button */}
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(true)}
          disabled={disabled}
          className={cn(
            'w-full flex items-center justify-between rounded-lg border border-gray-300 px-4 py-3',
            'text-left min-h-[48px]',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'disabled:bg-gray-100 disabled:cursor-not-allowed',
            error && 'border-red-500 focus:ring-red-500',
            !displayValue && 'text-gray-400'
          )}
        >
          <span>{displayValue || placeholder}</span>
          <Calendar className="h-5 w-5 text-gray-400" />
        </button>

        {/* Hidden input for form compatibility */}
        <input
          ref={ref}
          type="hidden"
          value={value || ''}
          onChange={(e) => onChange?.(e.target.value)}
        />

        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}

        {/* Bottom Sheet Calendar */}
        {isOpen && (
          <div className="fixed inset-0 z-50 flex flex-col justify-end">
            {/* Overlay */}
            <div
              className="fixed inset-0 bg-black bg-opacity-50 animate-in fade-in duration-200"
              onClick={() => setIsOpen(false)}
            />

            {/* Calendar Sheet */}
            <div className="relative bg-white rounded-t-2xl animate-in slide-in-from-bottom duration-300 pb-[env(safe-area-inset-bottom)]">
              {/* Handle */}
              <div className="flex justify-center pt-3 pb-2">
                <div className="w-10 h-1 bg-gray-300 rounded-full" />
              </div>

              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900">Select Date</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-400 -mr-2"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Month Navigation */}
              <div className="flex items-center justify-between px-4 py-3">
                <button
                  onClick={handlePrevMonth}
                  className="min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronLeft className="h-6 w-6" />
                </button>
                <span className="text-lg font-medium text-gray-900">
                  {MONTHS[viewMonth]} {viewYear}
                </span>
                <button
                  onClick={handleNextMonth}
                  className="min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  <ChevronRight className="h-6 w-6" />
                </button>
              </div>

              {/* Calendar Grid */}
              <div className="px-4 pb-4">
                {/* Day headers */}
                <div className="grid grid-cols-7 gap-1 mb-2">
                  {DAYS.map((day) => (
                    <div
                      key={day}
                      className="h-10 flex items-center justify-center text-xs font-medium text-gray-500"
                    >
                      {day}
                    </div>
                  ))}
                </div>

                {/* Days */}
                <div className="grid grid-cols-7 gap-1">
                  {calendarDays.map((day, index) => {
                    if (day === null) {
                      return <div key={`empty-${index}`} className="h-12" />
                    }

                    const isDayDisabled = isDateDisabled(day)
                    const isDayToday = isToday(day)
                    const isDaySelected = isSelected(day)

                    return (
                      <button
                        key={day}
                        type="button"
                        onClick={() => !isDayDisabled && handleDateSelect(day)}
                        disabled={isDayDisabled}
                        className={cn(
                          'h-12 flex items-center justify-center rounded-full text-sm font-medium',
                          'transition-colors',
                          isDayDisabled && 'text-gray-300 cursor-not-allowed',
                          !isDayDisabled && !isDaySelected && 'hover:bg-gray-100',
                          isDayToday && !isDaySelected && 'text-blue-600 font-bold',
                          isDaySelected && 'bg-blue-600 text-white'
                        )}
                      >
                        {day}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 px-4 py-4 border-t border-gray-100">
                <Button
                  variant="outline"
                  onClick={handleClear}
                  className="flex-1 min-h-[48px]"
                >
                  Clear
                </Button>
                <Button
                  variant="primary"
                  onClick={handleConfirm}
                  disabled={!selectedDate}
                  className="flex-1 min-h-[48px]"
                >
                  Confirm
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }
)

MobileDatePicker.displayName = 'MobileDatePicker'
