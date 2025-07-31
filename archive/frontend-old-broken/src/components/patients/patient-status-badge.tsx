import { cn } from '@/lib/utils'
import type { PatientStatus } from '@/types/patient'

interface PatientStatusBadgeProps {
  status: PatientStatus
  className?: string
}

const statusConfig = {
  ACTIVE: { 
    label: 'Active', 
    className: 'bg-green-500/10 text-green-500 border-green-500/50' 
  },
  INQUIRY: { 
    label: 'Inquiry', 
    className: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/50' 
  },
  ONBOARDING: { 
    label: 'Onboarding', 
    className: 'bg-blue-500/10 text-blue-500 border-blue-500/50' 
  },
  CHURNED: { 
    label: 'Churned', 
    className: 'bg-red-500/10 text-red-500 border-red-500/50' 
  },
}

export function PatientStatusBadge({ status, className }: PatientStatusBadgeProps) {
  const config = statusConfig[status]
  
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        config.className,
        className
      )}
    >
      {config.label}
    </span>
  )
}