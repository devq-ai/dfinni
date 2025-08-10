'use client'

import { useState, useEffect } from 'react'

export default function TestPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    fetch('/api/proxy/dashboard-stats')
      .then(res => res.json())
      .then(data => {
        console.log('Test page received data:', data)
        setData(data)
      })
      .catch(err => {
        console.error('Test page error:', err)
        setError(err.message)
      })
  }, [])
  
  return (
    <div className="p-4">
      <h1>Test Dashboard Data</h1>
      {error && <p className="text-red-500">Error: {error}</p>}
      <pre className="bg-gray-100 p-4 rounded mt-4">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}