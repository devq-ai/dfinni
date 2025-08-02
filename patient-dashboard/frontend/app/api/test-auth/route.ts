import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const { userId, sessionId, getToken } = await auth()
    const token = await getToken()
    
    return NextResponse.json({
      userId,
      sessionId,
      hasToken: !!token,
      tokenPreview: token ? token.substring(0, 20) + '...' : null
    })
  } catch (error) {
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}