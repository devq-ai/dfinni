// Created: 2025-08-05T22:45:00-06:00
import { NextResponse } from 'next/server';

export async function GET() {
  const environment = process.env.NODE_ENV;
  const isProduction = environment === 'production';
  
  // Basic health check
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment,
    version: process.env.npm_package_version || '1.0.0',
    uptime: process.uptime(),
  };
  
  // In production, check critical services
  if (isProduction) {
    try {
      // Check Clerk
      const clerkKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
      if (!clerkKey || !clerkKey.startsWith('pk_')) {
        throw new Error('Clerk configuration invalid');
      }
      
      // Check API endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiUrl) {
        throw new Error('API URL not configured');
      }
      
      return NextResponse.json(health);
    } catch (error) {
      return NextResponse.json(
        {
          status: 'unhealthy',
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
        },
        { status: 503 }
      );
    }
  }
  
  // Development includes more details
  return NextResponse.json({
    ...health,
    debug: {
      nodeVersion: process.version,
      platform: process.platform,
      memory: process.memoryUsage(),
    },
  });
}