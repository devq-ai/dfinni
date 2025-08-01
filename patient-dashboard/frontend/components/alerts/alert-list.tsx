'use client'

import { useState, useEffect } from 'react'
import { Alert } from '@/types/alert'
import { alertsApi } from '@/lib/api/alerts'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, AlertTriangle, Info, Clock, User } from 'lucide-react'

export function AlertList() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    loadAlerts()
  }, [filter])

  const loadAlerts = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await alertsApi.getAlerts(1, 50, filter === 'all' ? undefined : filter)
      setAlerts(response.alerts)
    } catch (err) {
      setError('Failed to load alerts')
      console.error('Error loading alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAcknowledge = async (alertId: string) => {
    try {
      const updatedAlert = await alertsApi.acknowledgeAlert(alertId)
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? updatedAlert : alert
      ))
    } catch (err) {
      console.error('Error acknowledging alert:', err)
    }
  }

  const handleResolve = async (alertId: string) => {
    try {
      const updatedAlert = await alertsApi.resolveAlert(alertId)
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? updatedAlert : alert
      ))
    } catch (err) {
      console.error('Error resolving alert:', err)
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default:
        return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  const getTypeVariant = (type: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (type) {
      case 'clinical': return 'destructive'
      case 'insurance': return 'secondary'
      default: return 'outline'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-muted-foreground">Loading alerts...</div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e] p-4">
        <p className="text-destructive">{error}</p>
        <Button
          onClick={loadAlerts}
          variant="outline"
          size="sm"
          className="mt-2 border-[#3e3e3e]"
        >
          Try again
        </Button>
      </Card>
    )
  }

  return (
    <div>
      {/* Filter Tabs */}
      <div className="border-b border-[#3e3e3e] mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setFilter('all')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              filter === 'all'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-[#3e3e3e]'
            }`}
          >
            All Alerts ({alerts.length})
          </button>
          <button
            onClick={() => setFilter('new')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              filter === 'new'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-[#3e3e3e]'
            }`}
          >
            New ({alerts.filter(a => a.status === 'new').length})
          </button>
          <button
            onClick={() => setFilter('acknowledged')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              filter === 'acknowledged'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground hover:border-[#3e3e3e]'
            }`}
          >
            Acknowledged ({alerts.filter(a => a.status === 'acknowledged').length})
          </button>
        </nav>
      </div>

      {/* Alert List */}
      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No alerts to display</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <Card
              key={alert.id}
              className={`bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e] p-6 ${
                alert.status === 'resolved' ? 'opacity-50' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {getSeverityIcon(alert.severity)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-lg font-medium">
                        {alert.title}
                      </h3>
                      <Badge variant={getTypeVariant(alert.type)}>
                        {alert.type}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {alert.description}
                    </p>
                    {alert.patientName && (
                      <div className="mt-2 flex items-center text-sm text-muted-foreground">
                        <User className="mr-1.5 h-4 w-4" />
                        <Link
                          href={`/patients/${alert.patientId}`}
                          className="hover:text-foreground transition-colors"
                        >
                          {alert.patientName}
                        </Link>
                      </div>
                    )}
                    <div className="mt-2 flex items-center text-sm text-muted-foreground">
                      <Clock className="mr-1.5 h-4 w-4" />
                      {new Date(alert.createdAt).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex-shrink-0 flex items-center space-x-2">
                  {alert.status === 'new' && (
                    <Button
                      onClick={() => handleAcknowledge(alert.id)}
                      variant="outline"
                      size="sm"
                      className="border-[#3e3e3e]"
                    >
                      Acknowledge
                    </Button>
                  )}
                  {alert.status !== 'resolved' && (
                    <Button
                      onClick={() => handleResolve(alert.id)}
                      size="sm"
                    >
                      Resolve
                    </Button>
                  )}
                  {alert.status === 'resolved' && (
                    <Badge variant="secondary">
                      Resolved
                    </Badge>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}