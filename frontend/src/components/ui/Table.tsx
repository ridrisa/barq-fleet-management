import { ReactNode, useState } from 'react'
import { cn } from '@/lib/cn'
import { ChevronUp, ChevronDown, ChevronRight } from 'lucide-react'
import { useMobile } from '@/hooks/useMobile'

export interface Column<T> {
  key: keyof T | string
  header?: ReactNode
  label?: string // Alias for header
  render?: (row: T) => ReactNode
  sortable?: boolean
  width?: string
  // Mobile-specific options
  priority?: 'primary' | 'secondary' | 'hidden' // Controls visibility on mobile
  mobileLabel?: string // Override label for mobile card view
}

export interface TableProps<T> {
  data: T[]
  columns: Column<T>[]
  onRowClick?: (row: T) => void
  isLoading?: boolean
  emptyMessage?: string
  sortColumn?: string
  sortDirection?: 'asc' | 'desc'
  onSort?: (column: string) => void
  // Mobile card customization
  mobileCardRender?: (row: T, columns: Column<T>[]) => ReactNode
  expandable?: boolean
}

// Mobile Card Row Component
function MobileCardRow<T extends object>({
  row,
  columns,
  onRowClick,
  expandable = true,
  customRender,
}: {
  row: T
  columns: Column<T>[]
  onRowClick?: (row: T) => void
  expandable?: boolean
  customRender?: (row: T, columns: Column<T>[]) => ReactNode
}) {
  const [isExpanded, setIsExpanded] = useState(false)

  const primaryColumns = columns.filter(
    (col) => col.priority === 'primary' || !col.priority
  )
  const secondaryColumns = columns.filter((col) => col.priority === 'secondary')
  const hasSecondary = secondaryColumns.length > 0

  const getValue = (column: Column<T>) => {
    if (column.render) {
      return column.render(row)
    }
    return String((row as Record<string, unknown>)[column.key as string] ?? '')
  }

  const handleClick = () => {
    if (onRowClick) {
      onRowClick(row)
    } else if (expandable && hasSecondary) {
      setIsExpanded(!isExpanded)
    }
  }

  if (customRender) {
    return (
      <div
        onClick={handleClick}
        className={cn(
          'bg-white rounded-lg border border-gray-200 p-4 mb-3 shadow-sm',
          'active:bg-gray-50 transition-colors',
          (onRowClick || (expandable && hasSecondary)) && 'cursor-pointer'
        )}
      >
        {customRender(row, columns)}
      </div>
    )
  }

  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200 mb-3 shadow-sm overflow-hidden',
        'active:bg-gray-50 transition-colors'
      )}
    >
      {/* Primary content - always visible */}
      <div
        onClick={handleClick}
        className={cn(
          'p-4',
          (onRowClick || (expandable && hasSecondary)) && 'cursor-pointer'
        )}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0 space-y-2">
            {primaryColumns.slice(0, 3).map((column, idx) => (
              <div key={String(column.key)} className="flex flex-col">
                {idx > 0 && (
                  <span className="text-xs text-gray-500 mb-0.5">
                    {column.mobileLabel || column.label || column.header}
                  </span>
                )}
                <span
                  className={cn(
                    'truncate',
                    idx === 0 ? 'text-base font-medium text-gray-900' : 'text-sm text-gray-700'
                  )}
                >
                  {getValue(column)}
                </span>
              </div>
            ))}
          </div>
          {expandable && hasSecondary && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setIsExpanded(!isExpanded)
              }}
              className="p-2 -m-2 min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-400 hover:text-gray-600"
              aria-label={isExpanded ? 'Collapse details' : 'Expand details'}
            >
              <ChevronRight
                className={cn(
                  'h-5 w-5 transition-transform duration-200',
                  isExpanded && 'rotate-90'
                )}
              />
            </button>
          )}
        </div>
        {/* Show remaining primary columns */}
        {primaryColumns.length > 3 && (
          <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2">
            {primaryColumns.slice(3).map((column) => (
              <div key={String(column.key)} className="flex flex-col">
                <span className="text-xs text-gray-500">
                  {column.mobileLabel || column.label || column.header}
                </span>
                <span className="text-sm text-gray-700 truncate">{getValue(column)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Secondary content - expandable */}
      {isExpanded && hasSecondary && (
        <div className="px-4 pb-4 pt-0 border-t border-gray-100 bg-gray-50/50">
          <div className="pt-3 grid grid-cols-2 gap-3">
            {secondaryColumns.map((column) => (
              <div key={String(column.key)} className="flex flex-col">
                <span className="text-xs text-gray-500 mb-0.5">
                  {column.mobileLabel || column.label || column.header}
                </span>
                <span className="text-sm text-gray-700">{getValue(column)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Loading skeleton for mobile
function MobileLoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="bg-white rounded-lg border border-gray-200 p-4 animate-pulse">
          <div className="space-y-3">
            <div className="h-5 bg-gray-200 rounded w-3/4" />
            <div className="h-4 bg-gray-100 rounded w-1/2" />
            <div className="flex gap-4">
              <div className="h-4 bg-gray-100 rounded w-1/4" />
              <div className="h-4 bg-gray-100 rounded w-1/4" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export const Table = <T extends object>({
  data,
  columns,
  onRowClick,
  isLoading = false,
  emptyMessage = 'No data available',
  sortColumn,
  sortDirection,
  onSort,
  mobileCardRender,
  expandable = true,
}: TableProps<T>) => {
  const isMobile = useMobile('md') // < 768px

  // Mobile card view
  if (isMobile) {
    if (isLoading) {
      return <MobileLoadingSkeleton />
    }

    if (data.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500 bg-white rounded-lg border border-gray-200">
          {emptyMessage}
        </div>
      )
    }

    return (
      <div className="space-y-0">
        {data.map((row, rowIndex) => (
          <MobileCardRow
            key={rowIndex}
            row={row}
            columns={columns.filter((col) => col.priority !== 'hidden')}
            onRowClick={onRowClick}
            expandable={expandable}
            customRender={mobileCardRender}
          />
        ))}
      </div>
    )
  }

  // Desktop table view
  if (isLoading) {
    return (
      <div className="w-full">
        <div className="animate-pulse">
          <div className="h-12 bg-gray-200 rounded mb-2" />
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded mb-2" />
          ))}
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 bg-white rounded-lg border border-gray-200">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto bg-white rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column) => (
              <th
                key={String(column.key)}
                scope="col"
                className={cn(
                  'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                  column.sortable && onSort && 'cursor-pointer hover:bg-gray-100',
                  column.width
                )}
                onClick={() => {
                  if (column.sortable && onSort) {
                    onSort(String(column.key))
                  }
                }}
                aria-sort={
                  column.sortable && sortColumn === column.key
                    ? sortDirection === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : column.sortable
                    ? 'none'
                    : undefined
                }
                tabIndex={column.sortable && onSort ? 0 : undefined}
                role={column.sortable ? 'button' : undefined}
                onKeyDown={(e) => {
                  if (column.sortable && onSort && (e.key === 'Enter' || e.key === ' ')) {
                    e.preventDefault()
                    onSort(String(column.key))
                  }
                }}
              >
                <div className="flex items-center gap-2">
                  {column.header || column.label}
                  {column.sortable && sortColumn === column.key && (
                    <>
                      {sortDirection === 'asc' ? (
                        <ChevronUp className="h-4 w-4" aria-hidden="true" />
                      ) : (
                        <ChevronDown className="h-4 w-4" aria-hidden="true" />
                      )}
                    </>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              onClick={() => onRowClick?.(row)}
              className={cn(
                'hover:bg-gray-50 transition-colors',
                onRowClick && 'cursor-pointer'
              )}
            >
              {columns.map((column) => (
                <td
                  key={String(column.key)}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  {column.render ? column.render(row) : String((row as Record<string, unknown>)[column.key as string] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
