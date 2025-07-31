import { useCallback } from 'react'
import { errorHandler, ApplicationError, ErrorContext } from '@/lib/error-handler'

export function useAsyncError() {
  return useCallback((error: unknown, context?: Partial<ErrorContext>) => {
    const appError = errorHandler.handleError(error, context)
    throw appError
  }, [])
}

export function useApiError() {
  return useCallback((
    error: unknown,
    endpoint: string,
    method: string,
    context?: Partial<ErrorContext>
  ) => {
    const appError = errorHandler.handleApiError(error, endpoint, method, context)
    throw appError
  }, [])
}