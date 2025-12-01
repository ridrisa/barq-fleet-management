import { ReactNode } from 'react'
import { Card, CardContent } from './Card'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/cn'

export interface KPICardProps {
  title: string
  value: string | number
  change?: number
  trend?: 'up' | 'down'
  icon?: ReactNode
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple' | 'indigo'
  className?: string
  loading?: boolean
}

const colorClasses = {
  blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
  green: 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400',
  yellow: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400',
  red: 'bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400',
  purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
  indigo: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400',
}

export function KPICard({
  title,
  value,
  change,
  trend,
  icon,
  color = 'blue',
  className,
  loading = false,
}: KPICardProps) {
  const trendIcon = trend === 'up' ? TrendingUp : TrendingDown
  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600'
  const TrendIcon = trendIcon

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              {title}
            </p>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              {value}
            </p>

            {(change !== undefined || trend) && (
              <div className="flex items-center gap-1.5">
                {trend && (
                  <TrendIcon
                    className={cn('w-4 h-4', trendColor)}
                    aria-hidden="true"
                  />
                )}
                {change !== undefined && (
                  <span
                    className={cn(
                      'text-sm font-medium',
                      change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                    )}
                  >
                    {change >= 0 ? '+' : ''}{change}%
                  </span>
                )}
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  vs last period
                </span>
              </div>
            )}
          </div>

          {icon && (
            <div
              className={cn(
                'p-3 rounded-lg transition-colors',
                colorClasses[color]
              )}
              aria-hidden="true"
            >
              {icon}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Alternative compact variant
export interface CompactKPICardProps extends KPICardProps {
  description?: string
}

export function CompactKPICard({
  title,
  value,
  change,
  trend,
  icon,
  color = 'blue',
  className,
  description,
  loading = false,
}: CompactKPICardProps) {
  if (loading) {
    return (
      <div className={cn('p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700', className)}>
        <div className="animate-pulse">
          <div className="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow',
        className
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">
            {title}
          </p>
        </div>
        {icon && (
          <div className={cn('p-2 rounded-md text-sm', colorClasses[color])}>
            {icon}
          </div>
        )}
      </div>

      <div className="space-y-1">
        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
          {value}
        </p>

        {description && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {description}
          </p>
        )}

        {(change !== undefined || trend) && (
          <div className="flex items-center gap-1">
            {change !== undefined && (
              <span
                className={cn(
                  'text-xs font-medium',
                  change >= 0 ? 'text-green-600' : 'text-red-600'
                )}
              >
                {change >= 0 ? '+' : ''}{change}%
              </span>
            )}
            {trend && (
              <span className="text-xs text-gray-500">
                {trend === 'up' ? '↑' : '↓'}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
