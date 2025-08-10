// Last Updated: 2025-08-10T02:40:00-06:00
'use client'

import { useState, useEffect } from 'react'

export default function SimpleDashboard() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    fetch('/api/proxy/dashboard-stats')
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.toString())
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="p-8">Loading dashboard data...</div>
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Simple Dashboard</h1>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border rounded">
          <h2 className="font-semibold">Total Patients</h2>
          <p className="text-3xl">{data?.current?.totalPatients || 0}</p>
          <p className="text-sm text-green-500">{data?.trends?.totalPatients?.value || '0%'}</p>
        </div>
        
        <div className="p-4 border rounded">
          <h2 className="font-semibold">Active Patients</h2>
          <p className="text-3xl">{data?.current?.activePatients || 0}</p>
          <p className="text-sm text-green-500">{data?.trends?.activePatients?.value || '0%'}</p>
        </div>
        
        <div className="p-4 border rounded">
          <h2 className="font-semibold">High Risk Patients</h2>
          <p className="text-3xl">{data?.current?.highRiskPatients || 0}</p>
          <p className="text-sm text-green-500">{data?.trends?.highRiskPatients?.value || '0%'}</p>
        </div>
        
        <div className="p-4 border rounded">
          <h2 className="font-semibold">Appointments Today</h2>
          <p className="text-3xl">{data?.current?.appointmentsToday || 0}</p>
          <p className="text-sm text-gray-500">{data?.trends?.appointmentsToday?.value || '0%'}</p>
        </div>
      </div>
      
      <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded">
        <h3 className="font-semibold mb-2">Raw Data:</h3>
        <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  )
}