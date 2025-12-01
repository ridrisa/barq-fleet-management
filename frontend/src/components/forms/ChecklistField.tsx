import { useState } from 'react'
import { Plus, Trash2, Check, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/cn'

export interface ChecklistItem {
  id: string
  label: string
  checked: boolean
}

export interface ChecklistFieldProps {
  items: ChecklistItem[]
  onChange: (items: ChecklistItem[]) => void
  allowAdd?: boolean
  allowRemove?: boolean
  title?: string
  className?: string
}

export const ChecklistField = ({
  items,
  onChange,
  allowAdd = true,
  allowRemove = true,
  title,
  className,
}: ChecklistFieldProps) => {
  const [newItemText, setNewItemText] = useState('')

  const handleToggle = (id: string) => {
    onChange(
      items.map(item =>
        item.id === id ? { ...item, checked: !item.checked } : item
      )
    )
  }

  const handleAdd = () => {
    if (!newItemText.trim()) return

    const newItem: ChecklistItem = {
      id: Date.now().toString(),
      label: newItemText.trim(),
      checked: false,
    }

    onChange([...items, newItem])
    setNewItemText('')
  }

  const handleRemove = (id: string) => {
    onChange(items.filter(item => item.id !== id))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAdd()
    }
  }

  const checkedCount = items.filter(item => item.checked).length
  const totalCount = items.length
  const progress = totalCount > 0 ? (checkedCount / totalCount) * 100 : 0

  return (
    <div className={cn('space-y-4', className)}>
      {title && (
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-700">{title}</h4>
          <span className="text-sm text-gray-500">
            {checkedCount} / {totalCount} completed
          </span>
        </div>
      )}

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-green-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Checklist items */}
      <div className="space-y-2">
        {items.map(item => (
          <div
            key={item.id}
            className={cn(
              'flex items-center gap-3 p-3 rounded-lg border transition-colors',
              item.checked
                ? 'bg-green-50 border-green-200'
                : 'bg-white border-gray-200 hover:border-gray-300'
            )}
          >
            <button
              type="button"
              onClick={() => handleToggle(item.id)}
              className={cn(
                'flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors',
                item.checked
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-300 hover:border-gray-400'
              )}
            >
              {item.checked && <Check className="w-4 h-4" />}
            </button>

            <span
              className={cn(
                'flex-1 text-sm',
                item.checked ? 'text-gray-500 line-through' : 'text-gray-900'
              )}
            >
              {item.label}
            </span>

            {allowRemove && (
              <button
                type="button"
                onClick={() => handleRemove(item.id)}
                className="flex-shrink-0 p-1 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Add new item */}
      {allowAdd && (
        <div className="flex gap-2">
          <Input
            type="text"
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Add new item..."
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            onClick={handleAdd}
            disabled={!newItemText.trim()}
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      )}

      {/* Quick actions */}
      {items.length > 0 && (
        <div className="flex gap-2 pt-2 border-t">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onChange(items.map(item => ({ ...item, checked: true })))}
            className="text-green-600 hover:text-green-700"
          >
            <Check className="w-4 h-4 mr-1" />
            Check All
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onChange(items.map(item => ({ ...item, checked: false })))}
            className="text-gray-600 hover:text-gray-700"
          >
            <X className="w-4 h-4 mr-1" />
            Uncheck All
          </Button>
        </div>
      )}
    </div>
  )
}

// Quality Control specific checklist
export const QualityChecklistField = ({
  items,
  onChange,
  className,
}: Omit<ChecklistFieldProps, 'allowAdd' | 'allowRemove'>) => {
  const handleToggle = (id: string, value: 'pass' | 'fail' | null) => {
    onChange(
      items.map(item =>
        item.id === id ? { ...item, checked: value === 'pass' } : item
      )
    )
  }

  const passCount = items.filter(item => item.checked).length
  const totalCount = items.length

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700">Quality Checklist</h4>
        <span className="text-sm text-gray-500">
          {passCount} / {totalCount} passed
        </span>
      </div>

      <div className="space-y-2">
        {items.map(item => (
          <div
            key={item.id}
            className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 bg-white"
          >
            <span className="flex-1 text-sm text-gray-900">{item.label}</span>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handleToggle(item.id, 'pass')}
                className={cn(
                  'px-3 py-1 text-sm rounded-md border transition-colors',
                  item.checked
                    ? 'bg-green-500 text-white border-green-500'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-green-400'
                )}
              >
                Pass
              </button>
              <button
                type="button"
                onClick={() => handleToggle(item.id, 'fail')}
                className={cn(
                  'px-3 py-1 text-sm rounded-md border transition-colors',
                  !item.checked
                    ? 'bg-red-500 text-white border-red-500'
                    : 'bg-white text-gray-600 border-gray-300 hover:border-red-400'
                )}
              >
                Fail
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ChecklistField
