import { cn } from '@/lib/cn'

export interface RadioOption {
  value: string
  label: string
  helperText?: string
}

export interface RadioGroupProps {
  name: string
  label?: string
  options: RadioOption[]
  value?: string
  onChange?: (value: string) => void
  error?: string
}

export const RadioGroup = ({
  name,
  label,
  options,
  value,
  onChange,
  error,
}: RadioGroupProps) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      <div className="space-y-3">
        {options.map((option) => (
          <div key={option.value} className="flex items-start">
            <div className="flex items-center h-5">
              <input
                type="radio"
                name={name}
                value={option.value}
                checked={value === option.value}
                onChange={(e) => onChange?.(e.target.value)}
                className={cn(
                  'w-4 h-4 text-blue-600 bg-white border-gray-300',
                  'focus:ring-2 focus:ring-blue-500'
                )}
              />
            </div>
            <div className="ml-3">
              <label className="text-sm font-medium text-gray-700">
                {option.label}
              </label>
              {option.helperText && (
                <p className="text-sm text-gray-500">{option.helperText}</p>
              )}
            </div>
          </div>
        ))}
      </div>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}
