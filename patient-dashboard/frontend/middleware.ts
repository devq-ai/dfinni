// Updated: 2025-08-05T22:30:00-06:00
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

// Only these routes are accessible without authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/webhooks(.*)',
  '/api/test',
  '/diagnostic',
  '/clerk-debug',
  '/simple-signin',
  '/static-test',
  '/test-basic-clerk',
  '/clerk-debug-test',
  '/clerk-test'
]);

export default clerkMiddleware(async (auth, req) => {
  const { userId, redirectToSignIn } = await auth();

  // Protect all routes except the public ones
  if (!isPublicRoute(req) && !userId) {
    // For API routes, return 401 Unauthorized
    if (req.nextUrl.pathname.startsWith('/api')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    
    // For all other routes, redirect to sign-in
    const signInUrl = new URL('/sign-in', req.url);
    signInUrl.searchParams.set('redirect_url', req.url);
    return NextResponse.redirect(signInUrl);
  }
  
  // Logged in users trying to access auth pages get redirected to dashboard
  if (userId && (
    req.nextUrl.pathname.startsWith('/sign-in') || 
    req.nextUrl.pathname.startsWith('/sign-up')
  )) {
    return NextResponse.redirect(new URL('/dashboard', req.url));
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};