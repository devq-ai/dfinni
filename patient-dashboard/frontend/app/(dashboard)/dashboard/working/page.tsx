// Last Updated: 2025-08-09T22:08:00-06:00
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, AlertCircle, Activity, Calendar } from 'lucide-react'

async function getDashboardStats() {
  try {
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://pfinni.devq.ai' 
      : 'http://localhost:3000'
    
    const response = await fetch(`${baseUrl}/api/proxy/dashboard-stats`, {
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch stats')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Dashboard stats error:', error)
    return null
  }
}

export default async function WorkingDashboardPage() {
  const stats = await getDashboardStats()
  
  const dashboardCards = [
    {
      name: 'Total Patients',
      value: stats?.current?.totalPatients || 0,
      icon: Users,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
      trend: stats?.trends?.totalPatients
    },
    {
      name: 'Active Alerts',
      value: 0,
      icon: AlertCircle,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      trend: { value: '0%', isUp: false }
    },
    {
      name: 'High Risk Patients',
      value: stats?.current?.highRiskPatients || 0,
      icon: Activity,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
      trend: stats?.trends?.highRiskPatients
    },
    {
      name: 'Active Patients',
      value: stats?.current?.activePatients || 0,
      icon: Calendar,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
      trend: stats?.trends?.activePatients
    }
  ]
  
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's an overview of your patients.</p>
      </div>
      
      {!stats && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 text-yellow-600 dark:text-yellow-400 px-4 py-3 rounded-md">
          <p className="text-sm">Unable to load dashboard statistics. Please refresh the page.</p>
        </div>
      )}
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {dashboardCards.map((card) => {
          const Icon = card.icon
          return (
            <Card key={card.name} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {card.name}
                </CardTitle>
                <Icon className={`h-4 w-4 ${card.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{card.value}</div>
                {card.trend && (
                  <p className={`text-xs ${card.trend.isUp ? 'text-green-600' : 'text-red-600'}`}>
                    {card.trend.value} from last month
                  </p>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
      
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>All systems operational</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">API Server</span>
                <span className="text-sm text-green-500">● Online</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Database</span>
                <span className="text-sm text-green-500">● Connected</span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
            <CardDescription>Key metrics at a glance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Data Source</span>
                <span className="text-sm">SurrealDB</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Last Updated</span>
                <span className="text-sm">Just now</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}