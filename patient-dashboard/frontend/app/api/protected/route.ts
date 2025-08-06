import { requireAuth } from '@/lib/auth-helpers';
import { NextResponse } from 'next/server';

export async function GET() {
  const authResult = await requireAuth();
  
  // If authResult is a NextResponse, user is not authenticated
  if (authResult instanceof NextResponse) {
    return authResult;
  }
  
  // User is authenticated, authResult contains userId
  return NextResponse.json({
    message: 'This is a protected route',
    userId: authResult
  });
}