'use client'

import { useEffect, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { logger } from '@/lib/logfire'

type Theme = 'light' | 'dark' | 'system'

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>('dark')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    // Get initial theme from localStorage or system preference
    const savedTheme = localStorage.getItem('theme') as Theme
    if (savedTheme) {
      setTheme(savedTheme)
      applyTheme(savedTheme)
    } else {
      // Default to dark theme for healthcare dashboard
      setTheme('dark')
      applyTheme('dark')
    }
  }, [])

  const applyTheme = (newTheme: Theme) => {
    const root = window.document.documentElement
    
    if (newTheme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      root.classList.toggle('dark', systemTheme === 'dark')
    } else {
      root.classList.toggle('dark', newTheme === 'dark')
    }
  }

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    applyTheme(newTheme)
    
    logger.userAction('theme_toggle', {
      from: theme,
      to: newTheme
    })
  }

  // Avoid hydration mismatch
  if (!mounted) {
    return (
      <Button
        variant="secondary"
        size="sm"
        className="w-9 h-9 p-0"
        aria-label="Toggle theme"
      >
        <span className="h-5 w-5" />
      </Button>
    )
  }

  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={toggleTheme}
      className="w-9 h-9 p-0"
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? (
        <Sun className="h-5 w-5 text-zinc-400 hover:text-zinc-100 transition-colors" />
      ) : (
        <Moon className="h-5 w-5 text-zinc-600 hover:text-zinc-900 transition-colors" />
      )}
    </Button>
  )
}