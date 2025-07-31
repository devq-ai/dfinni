'use client'

import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { logger } from '@/lib/logfire'

interface MetricCardProps {
  title: string
  value: number | string
  change?: number
  changeType?: 'increase' | 'decrease' | 'neutral'
  icon?: React.ReactNode
  color?: string
  className?: string
  onClick?: () => void
}

export function MetricCard({
  title,
  value,
  change,
  changeType,
  icon,
  color = 'blue',
  className,
  onClick,
}: MetricCardProps) {
  const handleClick = () => {
    if (onClick) {
      logger.userAction('metric_card_click', { title })
      onClick()
    }
  }

  const getTrendIcon = () => {
    if (!changeType || change === undefined) return null

    switch (changeType) {
      case 'increase':
        return <TrendingUp className="h-4 w-4" />
      case 'decrease':
        return <TrendingDown className="h-4 w-4" />
      case 'neutral':
        return <Minus className="h-4 w-4" />
    }
  }

  const getTrendColor = () => {
    if (!changeType) return 'text-zinc-400'

    switch (changeType) {
      case 'increase':
        return 'text-green-500'
      case 'decrease':
        return 'text-red-500'
      case 'neutral':
        return 'text-zinc-400'
    }
  }

  const colorStyles = {
    blue: 'border-blue-500/20 bg-blue-500/5',
    green: 'border-green-500/20 bg-green-500/5',
    yellow: 'border-yellow-500/20 bg-yellow-500/5',
    red: 'border-red-500/20 bg-red-500/5',
    purple: 'border-purple-500/20 bg-purple-500/5',
  }

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-lg border p-6 transition-all',
        colorStyles[color as keyof typeof colorStyles] || colorStyles.blue,
        onClick && 'cursor-pointer hover:shadow-lg hover:scale-[1.02]',
        className
      )}
      onClick={handleClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-zinc-400">{title}</p>
          <p className="text-3xl font-bold text-zinc-100">{value}</p>
          {change !== undefined && (
            <div className={cn('flex items-center space-x-1 text-sm', getTrendColor())}>
              {getTrendIcon()}
              <span>
                {change > 0 ? '+' : ''}{change}%
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={cn('text-4xl opacity-20', `text-${color}-500`)}>
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}