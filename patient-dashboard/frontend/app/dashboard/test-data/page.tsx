// Last Updated: 2025-08-10T02:36:00-06:00
'use client'

import { useState, useEffect } from 'react'

export default function TestDataPage() {
  const [proxyData, setProxyData] = useState<any>(null)
  const [directData, setDirectData] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [logs, setLogs] = useState<string[]>([])

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `[${new Date().toISOString()}] ${message}`])
  }

  useEffect(() => {
    addLog('Component mounted')
    testDataFetching()
  }, [])

  const testDataFetching = async () => {
    // Test proxy endpoint
    try {
      addLog('Fetching from proxy endpoint...')
      const proxyResponse = await fetch('/api/proxy/dashboard-stats')
      addLog(`Proxy response status: ${proxyResponse.status}`)
      
      if (proxyResponse.ok) {
        const data = await proxyResponse.json()
        addLog(`Proxy data received: ${JSON.stringify(data)}`)
        setProxyData(data)
      } else {
        addLog(`Proxy error: ${proxyResponse.statusText}`)
      }
    } catch (err) {
      addLog(`Proxy fetch error: ${err}`)
      setError(`Proxy error: ${err}`)
    }

    // Test direct endpoint (will likely fail due to CORS)
    try {
      addLog('Fetching from direct endpoint...')
      const directResponse = await fetch('https://db.devq.ai/api/v1/test-dashboard-stats')
      addLog(`Direct response status: ${directResponse.status}`)
      
      if (directResponse.ok) {
        const data = await directResponse.json()
        addLog(`Direct data received: ${JSON.stringify(data)}`)
        setDirectData(data)
      } else {
        addLog(`Direct error: ${directResponse.statusText}`)
      }
    } catch (err) {
      addLog(`Direct fetch error: ${err}`)
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Dashboard Data Test</h1>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Debug Logs:</h2>
        <div className="bg-black text-green-400 p-4 rounded font-mono text-xs overflow-auto max-h-64">
          {logs.map((log, i) => (
            <div key={i}>{log}</div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <h2 className="text-xl font-semibold mb-2">Proxy Data (/api/proxy/dashboard-stats):</h2>
          <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-auto">
            {proxyData ? JSON.stringify(proxyData, null, 2) : 'Loading...'}
          </pre>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-2">Direct Data (db.devq.ai):</h2>
          <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-auto">
            {directData ? JSON.stringify(directData, null, 2) : 'Loading or blocked by CORS...'}
          </pre>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded">
          Error: {error}
        </div>
      )}
    </div>
  )
}