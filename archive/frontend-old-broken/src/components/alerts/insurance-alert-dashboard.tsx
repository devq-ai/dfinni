'use client'

import React, { useState, useEffect } from 'react'
import { insuranceAlertService, type InsuranceAlert } from '@/services/insurance-alert-service'
import { logger } from '@/lib/logfire'
import { 
  Shield, 
  AlertCircle, 
  AlertTriangle, 
  Info,
  Clock,
  CheckCircle,
  FileText,
  DollarSign,
  Filter,
  RefreshCw
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { formatDistanceToNow } from 'date-fns'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface InsuranceAlertDashboardProps {
  patientId?: string
  className?: string
}

export function InsuranceAlertDashboard({ 
  patientId,
  className 
}: InsuranceAlertDashboardProps) {
  const [alerts, setAlerts] = useState<InsuranceAlert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filterType, setFilterType] = useState<string>('all')
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('active')

  const fetchAlerts = React.useCallback(async () => {
    setIsLoading(true)
    try {
      const params: Record<string, string> = { status: filterStatus }
      if (patientId) params.patientId = patientId
      if (filterType !== 'all') params.type = filterType
      if (filterSeverity !== 'all') params.severity = filterSeverity

      const data = await insuranceAlertService.getInsuranceAlerts(params)
      setAlerts(data)
    } catch (error) {
      logger.error('Failed to fetch insurance alerts', error)
    } finally {
      setIsLoading(false)
    }
  }, [patientId, filterType, filterSeverity, filterStatus])

  useEffect(() => {
    logger.componentMount('InsuranceAlertDashboard', { patientId })
    fetchAlerts()
    
    return () => {
      logger.componentUnmount('InsuranceAlertDashboard')
    }
  }, [patientId, fetchAlerts])

  const handleAcknowledge = async (alertId: string) => {
    try {
      await insuranceAlertService.acknowledgeAlert(alertId)
      logger.userAction('acknowledge_insurance_alert', { alertId })
      fetchAlerts()
    } catch (error) {
      logger.error('Failed to acknowledge alert', error)
    }
  }

  const handleResolve = async (alertId: string) => {
    try {
      await insuranceAlertService.resolveAlert(alertId)
      logger.userAction('resolve_insurance_alert', { alertId })
      fetchAlerts()
    } catch (error) {
      logger.error('Failed to resolve alert', error)
    }
  }

  const getAlertIcon = (type: InsuranceAlert['type']) => {
    switch (type) {
      case 'eligibility':
        return <Shield className="h-5 w-5" />
      case 'coverage':
        return <AlertCircle className="h-5 w-5" />
      case 'claim':
        return <DollarSign className="h-5 w-5" />
      case 'authorization':
        return <FileText className="h-5 w-5" />
      case 'expiry':
        return <Clock className="h-5 w-5" />
    }
  }

  const getSeverityIcon = (severity: InsuranceAlert['severity']) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />
      case 'medium':
        return <Info className="h-4 w-4 text-yellow-500" />
      case 'low':
        return <Info className="h-4 w-4 text-blue-500" />
    }
  }

  const getSeverityColor = (severity: InsuranceAlert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'border-red-500/50 bg-red-500/10'
      case 'high':
        return 'border-orange-500/50 bg-orange-500/10'
      case 'medium':
        return 'border-yellow-500/50 bg-yellow-500/10'
      case 'low':
        return 'border-blue-500/50 bg-blue-500/10'
    }
  }

  const getPriorityBadge = (priority: InsuranceAlert['priority']) => {
    const colors = {
      URGENT: 'bg-red-500/20 text-red-400',
      HIGH: 'bg-orange-500/20 text-orange-400',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400',
      LOW: 'bg-zinc-700 text-zinc-300',
    }

    return (
      <span className={cn(
        "px-2 py-0.5 text-xs font-medium rounded-full",
        colors[priority]
      )}>
        {priority}
      </span>
    )
  }

  const getStatusBadge = (status: InsuranceAlert['status']) => {
    const colors = {
      active: 'bg-green-500/20 text-green-400',
      acknowledged: 'bg-blue-500/20 text-blue-400',
      resolved: 'bg-zinc-700 text-zinc-300',
      expired: 'bg-zinc-800 text-zinc-500',
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

  const alertStats = {
    total: alerts.length,
    critical: alerts.filter(a => a.severity === 'critical').length,
    high: alerts.filter(a => a.severity === 'high').length,
    requiresAction: alerts.filter(a => a.requiresAction).length,
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-zinc-100">
              Insurance Alerts
            </h3>
            <p className="text-sm text-zinc-400 mt-1">
              Monitor insurance-related notifications and actions
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchAlerts}
            disabled={isLoading}
          >
            <RefreshCw className={cn(
              "h-4 w-4 mr-2",
              isLoading && "animate-spin"
            )} />
            Refresh
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-zinc-800/50 rounded-lg p-3">
            <p className="text-sm text-zinc-400">Total Active</p>
            <p className="text-2xl font-bold text-zinc-100">{alertStats.total}</p>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <p className="text-sm text-red-400">Critical</p>
            <p className="text-2xl font-bold text-red-400">{alertStats.critical}</p>
          </div>
          <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3">
            <p className="text-sm text-orange-400">High Priority</p>
            <p className="text-2xl font-bold text-orange-400">{alertStats.high}</p>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
            <p className="text-sm text-yellow-400">Action Required</p>
            <p className="text-2xl font-bold text-yellow-400">{alertStats.requiresAction}</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center gap-4">
          <Filter className="h-5 w-5 text-zinc-400" />
          
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="eligibility">Eligibility</SelectItem>
              <SelectItem value="coverage">Coverage</SelectItem>
              <SelectItem value="claim">Claims</SelectItem>
              <SelectItem value="authorization">Authorization</SelectItem>
              <SelectItem value="expiry">Expiry</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterSeverity} onValueChange={setFilterSeverity}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Severities</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="acknowledged">Acknowledged</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="all">All Statuses</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
            <RefreshCw className="h-8 w-8 text-zinc-600 animate-spin mx-auto mb-4" />
            <p className="text-sm text-zinc-500">Loading insurance alerts...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
            <Shield className="h-8 w-8 text-zinc-600 mx-auto mb-4" />
            <p className="text-sm text-zinc-500">No insurance alerts found</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={cn(
                "bg-zinc-900 border rounded-lg p-4 transition-all",
                getSeverityColor(alert.severity),
                alert.status === 'resolved' && "opacity-60"
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1">
                  <div className={cn(
                    "p-2 rounded-lg",
                    getSeverityColor(alert.severity).replace('border-', 'bg-').replace('/50', '/20')
                  )}>
                    {getAlertIcon(alert.type)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      {getSeverityIcon(alert.severity)}
                      <h4 className="text-sm font-semibold text-zinc-100">
                        {alert.title}
                      </h4>
                      {getPriorityBadge(alert.priority)}
                      {getStatusBadge(alert.status)}
                    </div>
                    
                    <p className="text-sm text-zinc-400 mb-2">
                      {alert.description}
                    </p>
                    
                    {alert.message && (
                      <p className="text-xs text-zinc-500 mb-2">
                        {alert.message}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 text-xs text-zinc-500">
                      {alert.patientName && (
                        <span>Patient: {alert.patientName}</span>
                      )}
                      {alert.insuranceProvider && (
                        <span>Provider: {alert.insuranceProvider}</span>
                      )}
                      {alert.policyNumber && (
                        <span>Policy: {alert.policyNumber}</span>
                      )}
                      <span>
                        {formatDistanceToNow(new Date(alert.createdAt), { 
                          addSuffix: true 
                        })}
                      </span>
                    </div>

                    {alert.metadata && (
                      <div className="mt-2 p-2 bg-zinc-800/50 rounded text-xs text-zinc-400">
                        {alert.metadata.claimNumber && (
                          <div>Claim #: {alert.metadata.claimNumber}</div>
                        )}
                        {alert.metadata.claimAmount && (
                          <div>Amount: ${alert.metadata.claimAmount.toLocaleString()}</div>
                        )}
                        {alert.metadata.coveragePercentage && (
                          <div>Coverage: {alert.metadata.coveragePercentage}%</div>
                        )}
                        {alert.metadata.remainingBenefits && (
                          <div>Remaining Benefits: ${alert.metadata.remainingBenefits.toLocaleString()}</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {alert.status === 'active' && (
                  <div className="flex items-center gap-2 ml-4">
                    {alert.requiresAction && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAcknowledge(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleResolve(alert.id)}
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}