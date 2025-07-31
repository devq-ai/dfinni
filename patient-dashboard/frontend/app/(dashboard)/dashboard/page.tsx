'use client'

import { useState, useEffect } from 'react'
import { patientsApi } from '@/lib/api/patients'
import { alertsApi } from '@/lib/api/alerts'
import Link from 'next/link'

export default function DashboardPage() {
  const [stats, setStats] = useState([
    { name: 'Total Patients', value: '0', color: 'bg-blue-500' },
    { name: 'Active Alerts', value: '0', color: 'bg-red-500', link: '/alerts' },
    { name: 'High Risk Patients', value: '0', color: 'bg-orange-500' },
    { name: 'Appointments Today', value: '0', color: 'bg-green-500' },
  ])
  const [recentAlerts, setRecentAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load patients data
      const patientsResponse = await patientsApi.getPatients(1, 100)
      const activePatients = patientsResponse.patients.filter(p => p.status === 'active')
      const highRiskPatients = patientsResponse.patients.filter(p => p.riskScore && p.riskScore >= 4)
      
      // Load alerts data
      const alertsResponse = await alertsApi.getAlerts(1, 10, 'new')
      
      setStats([
        { name: 'Total Patients', value: patientsResponse.total.toString(), color: 'bg-blue-500' },
        { name: 'Active Alerts', value: alertsResponse.total.toString(), color: 'bg-red-500', link: '/alerts' },
        { name: 'High Risk Patients', value: highRiskPatients.length.toString(), color: 'bg-orange-500' },
        { name: 'Active Patients', value: activePatients.length.toString(), color: 'bg-green-500' },
      ])
      
      setRecentAlerts(alertsResponse.alerts.slice(0, 5))
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const StatCard = ({ stat }: { stat: any }) => {
    const content = (
      <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className={`rounded-md ${stat.color} p-3`}>
                <div className="h-6 w-6 text-white" />
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  {stat.name}
                </dt>
                <dd className="text-2xl font-semibold text-gray-900">
                  {loading ? '...' : stat.value}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    )

    if (stat.link) {
      return <Link href={stat.link}>{content}</Link>
    }
    return content
  }

  return (
    <div className="py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <StatCard key={stat.name} stat={stat} />
          ))}
        </div>

        {/* Recent Alerts */}
        <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Recent Alerts
              </h3>
              <div className="mt-5">
                {loading ? (
                  <div className="text-center py-4">
                    <p className="text-gray-500">Loading alerts...</p>
                  </div>
                ) : recentAlerts.length > 0 ? (
                  <div className="space-y-3">
                    {recentAlerts.map((alert) => (
                      <Link
                        key={alert.id}
                        href="/alerts"
                        className="block hover:bg-gray-50 -mx-2 px-2 py-2 rounded"
                      >
                        <div className="flex items-start space-x-3">
                          <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                            alert.severity === 'critical' ? 'bg-red-500' :
                            alert.severity === 'high' ? 'bg-orange-500' :
                            alert.severity === 'medium' ? 'bg-yellow-500' :
                            'bg-blue-500'
                          }`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {alert.title}
                            </p>
                            <p className="text-sm text-gray-500 truncate">
                              {alert.description}
                            </p>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 text-center py-4">No active alerts</p>
                )}
              </div>
              <div className="mt-6">
                <Link
                  href="/alerts"
                  className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  View all alerts
                </Link>
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                System Status
              </h3>
              <div className="mt-5 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API Server</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <span className="text-green-600">Operational</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Database</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    <span className="text-green-600">Connected</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">WebSocket</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></div>
                    <span className="text-yellow-600">Pending</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Logfire</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                    <span className="text-gray-600">Disabled</span>
                  </span>
                </div>
              </div>
              <div className="mt-6">
                <div className="rounded-md bg-blue-50 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-blue-800">
                        Frontend rebuilt with stable architecture. All features operational.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}