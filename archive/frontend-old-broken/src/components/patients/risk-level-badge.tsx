import { cn } from '@/lib/utils'
import type { RiskLevel } from '@/types/patient'

interface RiskLevelBadgeProps {
  level: RiskLevel
  className?: string
}

const riskConfig = {
  LOW: { 
    label: 'Low Risk', 
    className: 'text-green-500 font-mono' 
  },
  MEDIUM: { 
    label: 'Medium Risk', 
    className: 'text-yellow-500 font-mono' 
  },
  HIGH: { 
    label: 'High Risk', 
    className: 'text-red-500 font-mono' 
  },
}

export function RiskLevelBadge({ level, className }: RiskLevelBadgeProps) {
  const config = riskConfig[level]
  
  return (
    <span
      className={cn(
        'text-xs font-medium',
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  )
}