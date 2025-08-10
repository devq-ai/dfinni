'use client'

import { useState, useEffect } from 'react'

export default function DebugDashboardPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [alertsData, setAlertsData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const testDashboardAPI = async () => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://db.devq.ai'
    addLog(`API_BASE_URL: ${API_BASE_URL}`)
    
    try {
      addLog('Starting dashboard API test...')
      
      // Test dashboard stats
      addLog('Fetching dashboard stats...')
      const dashboardResponse = await fetch(`${API_BASE_URL}/api/v1/test-dashboard-stats`, {
        headers: {
          'Content-Type': 'application/json'
        },
      })
      
      addLog(`Dashboard response status: ${dashboardResponse.status}`)
      
      if (!dashboardResponse.ok) {
        const errorText = await dashboardResponse.text()
        throw new Error(`Dashboard API failed: ${dashboardResponse.status} - ${errorText}`)
      }
      
      const dashboardJson = await dashboardResponse.json()
      setDashboardData(dashboardJson)
      addLog(`Dashboard data received: ${JSON.stringify(dashboardJson, null, 2)}`)
      
      // Test alerts stats
      addLog('Fetching alerts stats...')
      const alertsResponse = await fetch(`${API_BASE_URL}/api/v1/test-alerts-stats`, {
        headers: {
          'Content-Type': 'application/json'
        },
      })
      
      addLog(`Alerts response status: ${alertsResponse.status}`)
      
      if (!alertsResponse.ok) {
        const errorText = await alertsResponse.text()
        throw new Error(`Alerts API failed: ${alertsResponse.status} - ${errorText}`)
      }
      
      const alertsJson = await alertsResponse.json()
      setAlertsData(alertsJson)
      addLog(`Alerts data received: ${JSON.stringify(alertsJson, null, 2)}`)
      
      addLog('✅ All API tests completed successfully!')
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      addLog(`❌ Error: ${errorMessage}`)
      setError(errorMessage)
      console.error('API test error:', error)
    }
  }

  const testProductionDashboard = async () => {
    try {
      addLog('Testing how the production dashboard component would process this data...')
      
      if (!dashboardData) {
        addLog('❌ No dashboard data available')
        return
      }
      
      // Simulate the exact same processing as the production dashboard
      const alertsTotal = alertsData?.data?.stats?.total || alertsData?.total || 0
      const alertsList = alertsData?.data?.alerts || alertsData?.alerts || []
      
      addLog(`Production dashboard would show:`)
      addLog(`- Total Patients: ${dashboardData.current.totalPatients}`)
      addLog(`- Active Patients: ${dashboardData.current.activePatients}`)  
      addLog(`- High Risk Patients: ${dashboardData.current.highRiskPatients}`)
      addLog(`- Active Alerts: ${alertsTotal}`)
      addLog(`- Recent Alerts Count: ${alertsList.length}`)
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      addLog(`❌ Production simulation error: ${errorMessage}`)
    }
  }

  useEffect(() => {
    testDashboardAPI()
  }, [])

  useEffect(() => {
    if (dashboardData && alertsData) {
      testProductionDashboard()
    }
  }, [dashboardData, alertsData])

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Dashboard API Debug Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => {
          setLogs([])
          setDashboardData(null)
          setAlertsData(null)
          setError(null)
          testDashboardAPI()
        }}>
          Run Tests Again
        </button>
      </div>

      {error && (
        <div style={{ 
          background: '#ffebee', 
          border: '1px solid #f44336', 
          padding: '10px', 
          marginBottom: '20px',
          color: '#c62828'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ 
        background: '#f5f5f5', 
        padding: '15px', 
        border: '1px solid #ddd',
        maxHeight: '500px',
        overflowY: 'auto'
      }}>
        <h3>Debug Logs:</h3>
        {logs.map((log, index) => (
          <div key={index} style={{ marginBottom: '5px' }}>
            {log}
          </div>
        ))}
      </div>

      {dashboardData && (
        <div style={{ marginTop: '20px' }}>
          <h3>Dashboard Data Preview:</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
            <div style={{ background: '#e3f2fd', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{dashboardData.current.totalPatients}</div>
              <div>Total Patients</div>
            </div>
            <div style={{ background: '#f3e5f5', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{dashboardData.current.activePatients}</div>
              <div>Active Patients</div>
            </div>
            <div style={{ background: '#fff3e0', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{dashboardData.current.highRiskPatients}</div>
              <div>High Risk</div>
            </div>
            <div style={{ background: '#e8f5e8', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{alertsData?.data?.stats?.total || alertsData?.total || 0}</div>
              <div>Active Alerts</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}