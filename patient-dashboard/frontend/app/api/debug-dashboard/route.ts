// Last Updated: 2025-08-10T02:45:00-06:00
import { NextResponse } from 'next/server'

export async function GET() {
  // Test both proxy endpoints
  const tests = {
    dashboardStats: null as any,
    alertsStats: null as any,
    errors: [] as string[],
  }

  try {
    const dashResponse = await fetch('https://pfinni.devq.ai/api/proxy/dashboard-stats')
    tests.dashboardStats = {
      status: dashResponse.status,
      ok: dashResponse.ok,
      data: dashResponse.ok ? await dashResponse.json() : null
    }
  } catch (err) {
    tests.errors.push(`Dashboard stats error: ${err}`)
  }

  try {
    const alertsResponse = await fetch('https://pfinni.devq.ai/api/proxy/alerts-stats')
    tests.alertsStats = {
      status: alertsResponse.status,
      ok: alertsResponse.ok,
      data: alertsResponse.ok ? await alertsResponse.json() : null
    }
  } catch (err) {
    tests.errors.push(`Alerts stats error: ${err}`)
  }

  return NextResponse.json({
    timestamp: new Date().toISOString(),
    tests,
    env: {
      NODE_ENV: process.env.NODE_ENV,
      hasClerkKey: !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
      apiUrl: process.env.NEXT_PUBLIC_API_URL,
    }
  })
}