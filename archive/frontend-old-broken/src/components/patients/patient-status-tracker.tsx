'use client'

import { useEffect, useState } from 'react'
import { useWebSocketContext } from '@/contexts/websocket-context'
import { usePatientStore } from '@/stores/patient-store'
import { logger } from '@/lib/logfire'
import { Activity } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import type { Patient } from '@/types/patient'

interface StatusUpdate {
  patientId: string
  patientName: string
  oldStatus: string
  newStatus: string
  timestamp: string
}

export function PatientStatusTracker() {
  const { isConnected, subscribeToPatientUpdates, unsubscribeFromPatientUpdates } = useWebSocketContext()
  const { patients } = usePatientStore()
  const [recentUpdates, setRecentUpdates] = useState<StatusUpdate[]>([])
  const [isExpanded, setIsExpanded] = useState(true)

  useEffect(() => {
    // Subscribe to updates for all current patients
    if (isConnected && patients.length > 0) {
      patients.forEach(patient => {
        subscribeToPatientUpdates(patient.id)
      })

      logger.userAction('subscribed_to_all_patient_updates', { 
        count: patients.length 
      })

      // Cleanup subscriptions
      return () => {
        patients.forEach(patient => {
          unsubscribeFromPatientUpdates(patient.id)
        })
      }
    }
  }, [isConnected, patients, subscribeToPatientUpdates, unsubscribeFromPatientUpdates])

  // Listen for status updates via WebSocket
  useEffect(() => {
    const handleStatusUpdate = (event: CustomEvent<StatusUpdate>) => {
      logger.userAction('patient_status_update_received_in_tracker', { 
        patientId: event.detail.patientId 
      })
      
      setRecentUpdates(prev => [event.detail, ...prev].slice(0, 10)) // Keep last 10 updates
    }

    window.addEventListener('patient-status-update' as any, handleStatusUpdate)
    return () => {
      window.removeEventListener('patient-status-update' as any, handleStatusUpdate)
    }
  }, [])

  if (!isConnected) {
    return null
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-blue-500 animate-pulse" />
          <h3 className="text-sm font-semibold text-zinc-100">
            Live Status Updates
          </h3>
          {recentUpdates.length > 0 && (
            <span className="text-xs text-zinc-400">
              ({recentUpdates.length})
            </span>
          )}
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs text-zinc-400 hover:text-zinc-100"
        >
          {isExpanded ? 'Hide' : 'Show'}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-2">
          {recentUpdates.length === 0 ? (
            <p className="text-xs text-zinc-500 text-center py-4">
              Waiting for status updates...
            </p>
          ) : (
            recentUpdates.map((update, index) => (
              <div
                key={`${update.patientId}-${update.timestamp}`}
                className={cn(
                  "text-xs p-2 rounded-md bg-zinc-800/50 transition-all",
                  index === 0 && "ring-1 ring-blue-500/50 bg-blue-500/5"
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-medium text-zinc-100">
                      {update.patientName}
                    </span>
                    <span className="text-zinc-400 mx-1">•</span>
                    <span className="text-zinc-400">
                      {update.oldStatus} → {update.newStatus}
                    </span>
                  </div>
                  <span className="text-zinc-500 text-xs">
                    {formatDistanceToNow(new Date(update.timestamp), { 
                      addSuffix: true 
                    })}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}