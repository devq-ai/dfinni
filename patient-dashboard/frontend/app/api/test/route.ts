import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    message: 'API is working',
    basePath: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL?.includes('/pfinni') ? '/pfinni' : '',
    env: {
      NODE_ENV: process.env.NODE_ENV,
      NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? 'Set' : 'Not set',
      CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY ? 'Set' : 'Not set',
    },
    timestamp: new Date().toISOString()
  });
}