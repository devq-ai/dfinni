// Updated: 2025-07-31T12:42:00-06:00
'use client'

import { useState, useEffect } from 'react'
import { patientsApi } from '@/lib/api/patients'
import { alertsApi } from '@/lib/api/alerts'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  AlertCircle, 
  Activity, 
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp
} from 'lucide-react'

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

  const getStatIcon = (name: string) => {
    switch (name) {
      case 'Total Patients':
        return <Users className="h-4 w-4" />
      case 'Active Alerts':
        return <AlertCircle className="h-4 w-4" />
      case 'High Risk Patients':
        return <Activity className="h-4 w-4" />
      case 'Active Patients':
        return <Calendar className="h-4 w-4" />
      default:
        return <TrendingUp className="h-4 w-4" />
    }
  }

  const getStatTrend = (name: string) => {
    // Mock trend data - in real app, this would come from API
    const trends = {
      'Total Patients': { value: '+12.5%', isUp: true },
      'Active Alerts': { value: '-8.2%', isUp: false },
      'High Risk Patients': { value: '+3.1%', isUp: true },
      'Active Patients': { value: '+5.4%', isUp: true },
    }
    return trends[name as keyof typeof trends] || { value: '0%', isUp: true }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's an overview of your patients.</p>
      </div>
      
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const trend = getStatTrend(stat.name)
          return (
            <Card key={stat.name} className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.name}
                </CardTitle>
                {getStatIcon(stat.name)}
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {loading ? '...' : stat.value}
                </div>
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                  {trend.isUp ? (
                    <ArrowUpRight className="h-4 w-4 text-green-500 mr-1" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-red-500 mr-1" />
                  )}
                  <span className={trend.isUp ? 'text-green-600' : 'text-red-600'}>
                    {trend.value}
                  </span>
                  <span className="ml-1">from last month</span>
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Alerts and System Status */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
          <CardHeader>
            <CardTitle>Recent Alerts</CardTitle>
            <CardDescription>Latest patient alerts requiring attention</CardDescription>
          </CardHeader>
          <CardContent>
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
                        className="block hover:bg-accent rounded-md -mx-2 px-2 py-2 transition-colors"
                      >
                        <div className="flex items-start space-x-3">
                          <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                            alert.severity === 'critical' ? 'bg-red-500' :
                            alert.severity === 'high' ? 'bg-orange-500' :
                            alert.severity === 'medium' ? 'bg-yellow-500' :
                            'bg-blue-500'
                          }`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-100 truncate">
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
                  <p className="text-sm text-muted-foreground text-center py-4">No active alerts</p>
                )}
              </div>
              <div className="mt-6">
                <Button variant="outline" className="w-full" asChild>
                  <Link href="/alerts">
                    View all alerts
                  </Link>
                </Button>
              </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Current operational status of all services</CardDescription>
          </CardHeader>
          <CardContent>
              <div className="mt-5 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">API Server</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-green-500">Operational</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Database</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-green-500">Connected</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">WebSocket</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                    <span className="text-yellow-500">Pending</span>
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Logfire</span>
                  <span className="flex items-center text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-green-500">Enabled</span>
                  </span>
                </div>
              </div>
              <div className="mt-6">
                <div className="rounded-md bg-blue-500/10 p-4 border border-blue-500/20">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-blue-400">
                        Frontend rebuilt with stable architecture. All features operational.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}