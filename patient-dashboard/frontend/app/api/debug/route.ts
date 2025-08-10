import { NextResponse } from 'next/server';

export async function GET() {
  const env = {
    NODE_ENV: process.env.NODE_ENV,
    CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? 'SET' : 'NOT_SET',
    CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY ? 'SET' : 'NOT_SET',
    API_URL: process.env.NEXT_PUBLIC_API_URL,
  };

  return NextResponse.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    environment: env,
    runtime: 'nodejs',
  });
}