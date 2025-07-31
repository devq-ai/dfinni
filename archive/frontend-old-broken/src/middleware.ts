import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { edgeLogger as logger } from '@/lib/edge-logger'

// Define public routes that don't require authentication
const publicRoutes = [
  '/',
  '/login',
  '/reset-password',
  '/api/auth',
]

// Define role-based route access
const roleBasedRoutes: Record<string, string[]> = {
  '/settings/admin': ['admin'],
  '/audit': ['admin', 'audit'],
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Log the request
  logger.info('Middleware processing', {
    pathname,
    method: request.method,
    url: request.url,
  })

  // Check if route is public
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(`${route}/`)
  )

  if (isPublicRoute) {
    logger.info('Public route allowed', { pathname })
    return NextResponse.next()
  }

  // Check for auth token in cookies
  const token = request.cookies.get('auth-token')
  
  if (!token) {
    logger.warn('Unauthorized access attempt', { pathname })
    const redirectUrl = new URL('/login', request.url)
    redirectUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(redirectUrl)
  }

  // For role-based routes, we would need to decode the JWT token
  // and check user roles. For now, we'll just check if authenticated
  for (const [route, allowedRoles] of Object.entries(roleBasedRoutes)) {
    if (pathname.startsWith(route)) {
      // In a real implementation, decode token and check roles
      logger.info('Role-based route access', { pathname, allowedRoles })
    }
  }

  logger.info('Protected route - passing to client', { pathname })
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}