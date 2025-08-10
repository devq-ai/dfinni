/**
 * Central configuration for the frontend application
 */

export const config = {
  // API Configuration
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 
    (process.env.NODE_ENV === 'production' 
      ? 'https://db.devq.ai' 
      : 'http://localhost:8001'),
  
  // Application Name
  appName: 'PFINNI Patient Dashboard',
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  isProduction: process.env.NODE_ENV === 'production',
  isDevelopment: process.env.NODE_ENV === 'development',
  
  // Feature Flags
  features: {
    aiChat: true,
    realTimeAlerts: true,
    insuranceIntegration: true,
    birthdayAlerts: true,
  },
  
  // Clerk Configuration (populated at runtime)
  clerk: {
    publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '',
  },
}

// Helper function to get API endpoint
export function getApiEndpoint(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${config.apiUrl}${cleanPath}`
}

// Export for backward compatibility
export const API_BASE_URL = config.apiUrl