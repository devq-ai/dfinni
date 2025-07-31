'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/Button'
import { logger } from '@/lib/logfire'
import { 
  UserPlus, 
  FileText, 
  Download, 
  Bell,
  BarChart3,
  MessageSquare
} from 'lucide-react'

interface QuickAction {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  href?: string
  onClick?: () => void
  color: string
}

export function QuickActions() {
  const router = useRouter()

  const handleAction = (action: QuickAction) => {
    logger.userAction('quick_action_click', { 
      actionId: action.id,
      title: action.title 
    })
    
    if (action.href) {
      router.push(action.href)
    } else if (action.onClick) {
      action.onClick()
    }
  }

  const actions: QuickAction[] = [
    {
      id: 'add-patient',
      title: 'Add New Patient',
      description: 'Register a new patient in the system',
      icon: <UserPlus className="h-5 w-5" />,
      href: '/patients?action=new',
      color: 'blue',
    },
    {
      id: 'generate-report',
      title: 'Generate Report',
      description: 'Create analytics and insights report',
      icon: <FileText className="h-5 w-5" />,
      href: '/analytics?action=report',
      color: 'green',
    },
    {
      id: 'export-data',
      title: 'Export Data',
      description: 'Download patient data as CSV',
      icon: <Download className="h-5 w-5" />,
      onClick: () => {
        logger.userAction('export_data_initiated')
        // Export functionality would go here
      },
      color: 'purple',
    },
    {
      id: 'view-alerts',
      title: 'View Alerts',
      description: 'Check system and patient alerts',
      icon: <Bell className="h-5 w-5" />,
      href: '/alerts',
      color: 'yellow',
    },
    {
      id: 'analytics',
      title: 'Analytics Dashboard',
      description: 'View detailed analytics',
      icon: <BarChart3 className="h-5 w-5" />,
      href: '/analytics',
      color: 'indigo',
    },
    {
      id: 'ai-chat',
      title: 'AI Assistant',
      description: 'Chat with AI for insights',
      icon: <MessageSquare className="h-5 w-5" />,
      href: '/ai-insights',
      color: 'pink',
    },
  ]

  const colorStyles = {
    blue: 'hover:bg-blue-500/10 hover:border-blue-500/50 text-blue-500',
    green: 'hover:bg-green-500/10 hover:border-green-500/50 text-green-500',
    purple: 'hover:bg-purple-500/10 hover:border-purple-500/50 text-purple-500',
    yellow: 'hover:bg-yellow-500/10 hover:border-yellow-500/50 text-yellow-500',
    indigo: 'hover:bg-indigo-500/10 hover:border-indigo-500/50 text-indigo-500',
    pink: 'hover:bg-pink-500/10 hover:border-pink-500/50 text-pink-500',
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-zinc-100 mb-4">Quick Actions</h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => handleAction(action)}
            className={`
              flex items-start space-x-3 p-4 rounded-lg border border-zinc-800 
              transition-all hover:scale-[1.02] text-left
              ${colorStyles[action.color as keyof typeof colorStyles]}
            `}
          >
            <div className="flex-shrink-0 mt-0.5">
              {action.icon}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm">{action.title}</p>
              <p className="text-xs text-zinc-400 mt-0.5">
                {action.description}
              </p>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}