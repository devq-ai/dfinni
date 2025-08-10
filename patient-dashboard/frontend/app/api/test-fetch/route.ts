import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('https://db.devq.ai/api/v1/test-dashboard-stats', {
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `API returned ${response.status}` },
        { status: 500 }
      )
    }
    
    const data = await response.json()
    return NextResponse.json({ success: true, data })
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    )
  }
}