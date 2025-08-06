import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    message: 'Security headers are applied via middleware, not this route',
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    }
  });
}