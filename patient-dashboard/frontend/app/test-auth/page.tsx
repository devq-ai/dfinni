'use client'

import { useAuth } from '@clerk/nextjs'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function TestAuthPage() {
  const { getToken, isLoaded, isSignedIn, userId } = useAuth()
  const [token, setToken] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isSignedIn) {
      getToken().then(setToken)
    }
  }, [isSignedIn, getToken])

  const testBackendAuth = async () => {
    if (!token) return
    
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8001/api/v1/test-clerk', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      setTestResult(data)
    } catch (error) {
      setTestResult({ error: (error as Error).message })
    }
    setLoading(false)
  }

  if (!isLoaded) {
    return <div className="p-6">Loading...</div>
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Test Authentication</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Clerk Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p>Signed In: {isSignedIn ? 'Yes' : 'No'}</p>
            <p>User ID: {userId || 'Not signed in'}</p>
            <p>Token: {token ? `${token.substring(0, 50)}...` : 'No token'}</p>
          </div>
        </CardContent>
      </Card>

      {token && (
        <Card>
          <CardHeader>
            <CardTitle>Test Backend</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={testBackendAuth} disabled={loading}>
              {loading ? 'Testing...' : 'Test Backend Auth'}
            </Button>
            
            {testResult && (
              <div className="mt-4">
                <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-auto text-xs">
                  {JSON.stringify(testResult, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}