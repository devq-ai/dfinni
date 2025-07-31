'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'
import { logger } from '@/lib/logfire'

interface BreadcrumbProps {
  className?: string
}

export function Breadcrumb({ className }: BreadcrumbProps) {
  const pathname = usePathname()
  
  // Generate breadcrumb items from pathname
  const generateBreadcrumbs = () => {
    const paths = pathname.split('/').filter(Boolean)
    const breadcrumbs = [
      { label: 'Home', href: '/', icon: Home }
    ]
    
    let currentPath = ''
    paths.forEach((path) => {
      currentPath += `/${path}`
      const label = path
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
      
      breadcrumbs.push({
        label,
        href: currentPath,
        icon: null
      })
    })
    
    return breadcrumbs
  }
  
  const breadcrumbs = generateBreadcrumbs()
  
  const handleClick = (href: string, label: string) => {
    logger.userAction('breadcrumb_navigation', {
      from: pathname,
      to: href,
      label
    })
  }
  
  if (breadcrumbs.length <= 1) {
    return null // Don't show breadcrumbs on home page
  }
  
  return (
    <nav
      aria-label="Breadcrumb"
      className={cn("flex items-center space-x-2 text-sm", className)}
    >
      {breadcrumbs.map((breadcrumb, index) => {
        const isLast = index === breadcrumbs.length - 1
        const Icon = breadcrumb.icon
        
        return (
          <div key={breadcrumb.href} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="mx-2 h-4 w-4 text-zinc-500" />
            )}
            
            {isLast ? (
              <span className="flex items-center text-zinc-100 font-medium">
                {Icon && <Icon className="mr-1 h-4 w-4" />}
                {breadcrumb.label}
              </span>
            ) : (
              <Link
                href={breadcrumb.href}
                onClick={() => handleClick(breadcrumb.href, breadcrumb.label)}
                className="flex items-center text-zinc-400 hover:text-zinc-100 transition-colors"
              >
                {Icon && <Icon className="mr-1 h-4 w-4" />}
                {breadcrumb.label}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}