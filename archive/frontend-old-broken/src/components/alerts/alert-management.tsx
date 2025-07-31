'use client'

import React, { useState, useEffect } from 'react'
import { logger } from '@/lib/logfire'
import { 
  Bell, 
  Cake, 
  UserCheck, 
  Activity,
  Settings,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { formatDistanceToNow, addDays, format } from 'date-fns'
import { usePatientStore } from '@/stores/patient-store'

interface SystemAlert {
  id: string
  type: 'birthday' | 'status_change' | 'urgent_care' | 'appointment' | 'medication'
  title: string
  message: string
  patientId: string
  patientName: string
  triggerDate: string
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'sent' | 'acknowledged'
  createdAt: string
}

interface AlertPreferences {
  birthdayAlerts: {
    enabled: boolean
    daysBefore: number
  }
  statusChangeAlerts: {
    enabled: boolean
    statuses: string[]
  }
  urgentCareAlerts: {
    enabled: boolean
    autoEscalate: boolean
  }
}

export function AlertManagement() {
  const { patients } = usePatientStore()
  const [alerts, setAlerts] = useState<SystemAlert[]>([])
  const [preferences, setPreferences] = useState<AlertPreferences>({
    birthdayAlerts: {
      enabled: true,
      daysBefore: 7
    },
    statusChangeAlerts: {
      enabled: true,
      statuses: ['Active', 'Churned', 'Inquiry']
    },
    urgentCareAlerts: {
      enabled: true,
      autoEscalate: true
    }
  })
  const [isEditingPrefs, setIsEditingPrefs] = useState(false)

  const generateAlerts = React.useCallback(() => {
    const newAlerts: SystemAlert[] = []
    const now = new Date()
    
    // Generate birthday alerts
    if (preferences.birthdayAlerts.enabled) {
      patients.forEach(patient => {
        if (patient.dateOfBirth) {
          const dob = new Date(patient.dateOfBirth)
          const thisYearBirthday = new Date(now.getFullYear(), dob.getMonth(), dob.getDate())
          
          // If birthday already passed this year, check next year
          if (thisYearBirthday < now) {
            thisYearBirthday.setFullYear(thisYearBirthday.getFullYear() + 1)
          }
          
          const daysUntilBirthday = Math.ceil((thisYearBirthday.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
          
          if (daysUntilBirthday <= preferences.birthdayAlerts.daysBefore && daysUntilBirthday >= 0) {
            newAlerts.push({
              id: `bday-${patient.id}`,
              type: 'birthday',
              title: 'Upcoming Birthday',
              message: `${patient.firstName} ${patient.lastName}'s birthday is in ${daysUntilBirthday} days (${format(thisYearBirthday, 'MMM dd')})`,
              patientId: patient.id,
              patientName: `${patient.firstName} ${patient.lastName}`,
              triggerDate: thisYearBirthday.toISOString(),
              priority: daysUntilBirthday <= 2 ? 'high' : 'medium',
              status: 'pending',
              createdAt: now.toISOString()
            })
          }
        }
      })
    }

    // Generate status change alerts (mock recent changes)
    if (preferences.statusChangeAlerts.enabled) {
      const recentChanges = [
        { patientId: patients[0]?.id, name: patients[0] ? `${patients[0].firstName} ${patients[0].lastName}` : 'Unknown', oldStatus: 'Inquiry', newStatus: 'Active', daysAgo: 1 },
        { patientId: patients[1]?.id, name: patients[1] ? `${patients[1].firstName} ${patients[1].lastName}` : 'Unknown', oldStatus: 'Active', newStatus: 'Churned', daysAgo: 3 },
      ].filter(change => change.patientId && preferences.statusChangeAlerts.statuses.includes(change.newStatus))

      recentChanges.forEach((change, index) => {
        if (change.patientId) {
          newAlerts.push({
            id: `status-${index}`,
            type: 'status_change',
            title: 'Patient Status Changed',
            message: `${change.name} status changed from ${change.oldStatus} to ${change.newStatus}`,
            patientId: change.patientId,
            patientName: change.name,
            triggerDate: addDays(now, -change.daysAgo).toISOString(),
            priority: change.newStatus === 'Churned' ? 'high' : 'medium',
            status: 'sent',
            createdAt: addDays(now, -change.daysAgo).toISOString()
          })
        }
      })
    }

    // Generate urgent care alerts (mock)
    if (preferences.urgentCareAlerts.enabled && patients.length > 2) {
      newAlerts.push({
        id: 'urgent-1',
        type: 'urgent_care',
        title: 'Urgent Care Needed',
        message: `${patients[2].firstName} ${patients[2].lastName} has critical lab results requiring immediate attention`,
        patientId: patients[2].id,
        patientName: `${patients[2].firstName} ${patients[2].lastName}`,
        triggerDate: now.toISOString(),
        priority: 'high',
        status: 'pending',
        createdAt: addDays(now, -0.5).toISOString()
      })
    }

    setAlerts(newAlerts)
    logger.userAction('alerts_generated', { count: newAlerts.length })
  }, [patients, preferences])

  useEffect(() => {
    logger.componentMount('AlertManagement')
    generateAlerts()
    
    return () => {
      logger.componentUnmount('AlertManagement')
    }
  }, [generateAlerts])

  const handleAcknowledge = (alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, status: 'acknowledged' as const }
          : alert
      )
    )
    logger.userAction('acknowledge_system_alert', { alertId })
  }

  const getAlertIcon = (type: SystemAlert['type']) => {
    switch (type) {
      case 'birthday':
        return <Cake className="h-5 w-5 text-pink-500" />
      case 'status_change':
        return <UserCheck className="h-5 w-5 text-blue-500" />
      case 'urgent_care':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'appointment':
        return <Clock className="h-5 w-5 text-green-500" />
      case 'medication':
        return <Activity className="h-5 w-5 text-purple-500" />
    }
  }

  const getPriorityColor = (priority: SystemAlert['priority']) => {
    switch (priority) {
      case 'high':
        return 'border-red-500/50 bg-red-500/10'
      case 'medium':
        return 'border-yellow-500/50 bg-yellow-500/10'
      case 'low':
        return 'border-zinc-700/50 bg-zinc-800/50'
    }
  }

  const getStatusBadge = (status: SystemAlert['status']) => {
    const colors = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      sent: 'bg-blue-500/20 text-blue-400',
      acknowledged: 'bg-green-500/20 text-green-400',
    }

    return (
      <span className={cn(
        "px-2 py-0.5 text-xs font-medium rounded-full",
        colors[status]
      )}>
        {status}
      </span>
    )
  }

  return (
    <div className="space-y-4">
      {/* Alert Preferences */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-zinc-400" />
            <h3 className="text-sm font-semibold text-zinc-100">
              Alert Preferences
            </h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsEditingPrefs(!isEditingPrefs)}
          >
            {isEditingPrefs ? 'Save' : 'Edit'}
          </Button>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={preferences.birthdayAlerts.enabled}
                onChange={(e) => setPreferences(prev => ({
                  ...prev,
                  birthdayAlerts: { ...prev.birthdayAlerts, enabled: e.target.checked }
                }))}
                disabled={!isEditingPrefs}
                className="rounded border-zinc-700"
              />
              <span className="text-sm text-zinc-300">Birthday Alerts</span>
            </label>
            {isEditingPrefs && preferences.birthdayAlerts.enabled && (
              <div className="ml-6">
                <label className="text-xs text-zinc-500">
                  Days before:
                  <input
                    type="number"
                    value={preferences.birthdayAlerts.daysBefore}
                    onChange={(e) => setPreferences(prev => ({
                      ...prev,
                      birthdayAlerts: { ...prev.birthdayAlerts, daysBefore: parseInt(e.target.value) || 7 }
                    }))}
                    className="ml-2 w-12 px-1 py-0.5 bg-zinc-800 border border-zinc-700 rounded text-xs"
                  />
                </label>
              </div>
            )}
          </div>

          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={preferences.statusChangeAlerts.enabled}
                onChange={(e) => setPreferences(prev => ({
                  ...prev,
                  statusChangeAlerts: { ...prev.statusChangeAlerts, enabled: e.target.checked }
                }))}
                disabled={!isEditingPrefs}
                className="rounded border-zinc-700"
              />
              <span className="text-sm text-zinc-300">Status Change Alerts</span>
            </label>
          </div>

          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={preferences.urgentCareAlerts.enabled}
                onChange={(e) => setPreferences(prev => ({
                  ...prev,
                  urgentCareAlerts: { ...prev.urgentCareAlerts, enabled: e.target.checked }
                }))}
                disabled={!isEditingPrefs}
                className="rounded border-zinc-700"
              />
              <span className="text-sm text-zinc-300">Urgent Care Alerts</span>
            </label>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
            <Bell className="h-8 w-8 text-zinc-600 mx-auto mb-4" />
            <p className="text-sm text-zinc-500">No active alerts</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={cn(
                "bg-zinc-900 border rounded-lg p-4 transition-all",
                getPriorityColor(alert.priority),
                alert.status === 'acknowledged' && "opacity-60"
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  {getAlertIcon(alert.type)}
                  
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="text-sm font-semibold text-zinc-100">
                        {alert.title}
                      </h4>
                      {getStatusBadge(alert.status)}
                    </div>
                    
                    <p className="text-sm text-zinc-400 mb-2">
                      {alert.message}
                    </p>
                    
                    <div className="flex items-center gap-4 text-xs text-zinc-500">
                      <span>Patient: {alert.patientName}</span>
                      <span>
                        {formatDistanceToNow(new Date(alert.createdAt), { 
                          addSuffix: true 
                        })}
                      </span>
                    </div>
                  </div>
                </div>

                {alert.status !== 'acknowledged' && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleAcknowledge(alert.id)}
                  >
                    <CheckCircle className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}