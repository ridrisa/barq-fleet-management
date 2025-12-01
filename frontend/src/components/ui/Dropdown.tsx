import { ReactNode, useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/cn'
import { ChevronDown } from 'lucide-react'

export interface DropdownItem {
  id: string
  label: string
  icon?: ReactNode
  onClick: () => void
  danger?: boolean
  disabled?: boolean
}

export interface DropdownProps {
  trigger: ReactNode
  items: DropdownItem[]
  align?: 'left' | 'right'
}

export const Dropdown = ({ trigger, items, align = 'left' }: DropdownProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  return (
    <div ref={dropdownRef} className="relative inline-block">
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>

      {isOpen && (
        <div
          className={cn(
            'absolute z-50 mt-2 w-56 rounded-lg bg-white shadow-lg border border-gray-200 py-1',
            align === 'right' && 'right-0',
            align === 'left' && 'left-0'
          )}
        >
          {items.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                if (!item.disabled) {
                  item.onClick()
                  setIsOpen(false)
                }
              }}
              disabled={item.disabled}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-2 text-sm text-left transition-colors',
                item.danger
                  ? 'text-red-600 hover:bg-red-50'
                  : 'text-gray-700 hover:bg-gray-50',
                item.disabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export interface SelectDropdownProps {
  label: string
  value?: string
  options: { value: string; label: string }[]
  onChange: (value: string) => void
  placeholder?: string
}

export const SelectDropdown = ({
  label,
  value,
  options,
  onChange,
  placeholder = 'Select an option',
}: SelectDropdownProps) => {
  const selectedOption = options.find((opt) => opt.value === value)

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <Dropdown
        align="left"
        trigger={
          <button className="w-full flex items-center justify-between px-4 py-2 text-sm border border-gray-300 rounded-lg bg-white hover:bg-gray-50">
            <span className={cn(!selectedOption && 'text-gray-400')}>
              {selectedOption?.label || placeholder}
            </span>
            <ChevronDown className="h-4 w-4 text-gray-400" />
          </button>
        }
        items={options.map((option) => ({
          id: option.value,
          label: option.label,
          onClick: () => onChange(option.value),
        }))}
      />
    </div>
  )
}
