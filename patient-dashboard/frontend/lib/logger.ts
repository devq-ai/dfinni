// Simple logger that only works in browser environment
// No complex dependencies or browser APIs in Edge Runtime

const isDev = process.env.NODE_ENV === 'development'

interface LogContext {
  [key: string]: any
}

class Logger {
  private logToConsole(level: string, message: string, context?: LogContext) {
    if (!isDev) return
    
    const timestamp = new Date().toISOString()
    const contextStr = context ? JSON.stringify(context) : ''
    
    switch (level) {
      case 'info':
        console.log(`[${timestamp}] [INFO] ${message}`, contextStr)
        break
      case 'warn':
        console.warn(`[${timestamp}] [WARN] ${message}`, contextStr)
        break
      case 'error':
        console.error(`[${timestamp}] [ERROR] ${message}`, contextStr)
        break
      case 'debug':
        console.debug(`[${timestamp}] [DEBUG] ${message}`, contextStr)
        break
    }
  }

  info(message: string, context?: LogContext) {
    this.logToConsole('info', message, context)
  }

  warn(message: string, context?: LogContext) {
    this.logToConsole('warn', message, context)
  }

  error(message: string, error?: unknown, context?: LogContext) {
    const errorContext = {
      ...context,
      error: error instanceof Error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : error
    }
    this.logToConsole('error', message, errorContext)
  }

  debug(message: string, context?: LogContext) {
    this.logToConsole('debug', message, context)
  }
}

export const logger = new Logger()