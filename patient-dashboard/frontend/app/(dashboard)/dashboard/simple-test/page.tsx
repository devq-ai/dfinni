'use client'

import { useState, useEffect } from 'react'

export default function SimpleTestPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    
    fetch('https://db.devq.ai/api/v1/test-dashboard-stats', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      mode: 'cors',
      signal: controller.signal,
    })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message || 'Network error')
          setLoading(false)
        }
      })
    
    // Timeout after 3 seconds
    const timeout = setTimeout(() => {
      controller.abort()
      setError('Request timeout')
      setLoading(false)
    }, 3000)
    
    return () => {
      clearTimeout(timeout)
      controller.abort()
    }
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Simple Dashboard Test</h1>
      
      {loading && <p>Loading...</p>}
      
      {error && (
        <div className="bg-red-100 p-4 rounded">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}
      
      {data && (
        <div className="bg-green-100 p-4 rounded">
          <p className="text-green-700">Success! Total Patients: {data.current?.totalPatients || 'N/A'}</p>
          <pre className="text-xs mt-2">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}