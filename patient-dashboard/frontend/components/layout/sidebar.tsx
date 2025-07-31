// Updated: 2025-07-31T14:05:00-06:00
"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  LayoutDashboard, 
  Users, 
  Bell, 
  FileText,
  Settings,
  ChevronLeft,
  Menu
} from "lucide-react"
import { useState } from "react"

const sidebarItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Patients",
    href: "/patients",
    icon: Users,
  },
  {
    title: "Alerts",
    href: "/alerts",
    icon: Bell,
  },
  {
    title: "Reports",
    href: "/reports",
    icon: FileText,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <div
      className={cn(
        "relative flex h-full flex-col border-r border-border bg-sidebar transition-all duration-300 dark:bg-[#141414] dark:border-[#3e3e3e]",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-16 items-center justify-between border-b border-border px-4 dark:border-[#3e3e3e]">
        {!isCollapsed && (
          <Link href="/dashboard" className="flex items-center space-x-2">
            <span className="text-xl font-bold">PFINNI</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={cn(isCollapsed && "mx-auto")}
        >
          {isCollapsed ? <Menu className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-2">
          {sidebarItems.map((item) => {
            const Icon = item.icon
            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={pathname === item.href ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start",
                    isCollapsed && "justify-center px-2"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {!isCollapsed && <span className="ml-2">{item.title}</span>}
                </Button>
              </Link>
            )
          })}
        </nav>
      </ScrollArea>
    </div>
  )
}