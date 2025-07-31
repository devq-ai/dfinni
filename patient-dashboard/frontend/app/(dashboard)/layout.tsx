// Updated: 2025-07-31T14:05:00-06:00
import { ReactNode } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground dark:bg-[#0f0f0f] dark:text-white">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto bg-card p-4 md:p-6 lg:p-8 dark:bg-[#0f0f0f]">
          {children}
        </main>
      </div>
    </div>
  )
}