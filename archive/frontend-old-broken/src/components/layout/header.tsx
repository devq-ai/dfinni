'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/auth-store'
import { logger } from '@/lib/logfire'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/Button'
import { User, LogOut, Settings, Bell } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Breadcrumb } from './breadcrumb'
import { ThemeToggle } from './theme-toggle'
import { ConnectionStatus } from '@/components/websocket/connection-status'

interface HeaderProps {
  className?: string
}

export function Header({ className }: HeaderProps) {
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true)
      logger.userAction('logout_initiated', { userId: user?.id })
      await logout()
      router.push('/login')
    } catch (error) {
      logger.error('Logout failed', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  const handleMenuItemClick = (action: string, href?: string) => {
    logger.userAction('header_menu_click', { action, userId: user?.id })
    if (href) {
      router.push(href)
    }
  }

  return (
    <header 
      className={cn(
        "h-16 border-b border-zinc-800 bg-zinc-950",
        className
      )}
    >
      <div className="flex h-full items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left side - breadcrumbs */}
        <div className="flex items-center">
          <Breadcrumb />
        </div>

        {/* Right side - connection status, theme toggle, notifications and user menu */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <ConnectionStatus showLabel={false} />
          
          {/* Theme Toggle */}
          <ThemeToggle />
          
          {/* Notifications */}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => handleMenuItemClick('notifications', '/alerts')}
            className="relative"
            aria-label="View notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 ring-2 ring-zinc-950" />
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="secondary"
                size="sm"
                className="flex items-center space-x-2"
              >
                <User className="h-5 w-5" />
                <span className="hidden sm:inline-block">
                  {user?.name || user?.email || 'User'}
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-zinc-900 border-zinc-800">
              <DropdownMenuLabel className="text-zinc-400">
                My Account
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-zinc-800" />
              <DropdownMenuItem
                onClick={() => handleMenuItemClick('profile', '/settings/profile')}
                className="text-zinc-100 hover:bg-zinc-800 cursor-pointer"
              >
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => handleMenuItemClick('settings', '/settings')}
                className="text-zinc-100 hover:bg-zinc-800 cursor-pointer"
              >
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-zinc-800" />
              <DropdownMenuItem
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="text-zinc-100 hover:bg-zinc-800 cursor-pointer"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>{isLoggingOut ? 'Logging out...' : 'Log out'}</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}