'use client'

import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useWebSocket, UseWebSocketReturn } from '@/hooks/use-websocket'
import { WebSocketMessage } from '@/lib/websocket'
import { usePatientStore } from '@/stores/patient-store'
import { useDashboardStore } from '@/stores/dashboard-store'
import { logger } from '@/lib/logfire'
import { toast } from '@/lib/toast'

export interface WebSocketContextType extends UseWebSocketReturn {
  subscribeToPatientUpdates: (patientId: string) => void
  unsubscribeFromPatientUpdates: (patientId: string) => void
  subscribeToAlerts: () => void
  unsubscribeFromAlerts: () => void
}

export const WebSocketContext = createContext<WebSocketContextType | null>(null)

export function useWebSocketContext() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider')
  }
  return context
}

interface WebSocketProviderProps {
  children: ReactNode
}

export function WebSocketProvider({ children }: WebSocketProviderProps) {
  const { fetchPatients, updatePatient } = usePatientStore()
  const { fetchActivities, fetchMetrics } = useDashboardStore()

  const handleMessage = (message: WebSocketMessage) => {
    logger.userAction('websocket_message_processed', { 
      type: message.type,
      timestamp: message.timestamp 
    })

    switch (message.type) {
      case 'patient_status_update':
        handlePatientStatusUpdate(message.data)
        break
      case 'new_alert':
        handleNewAlert(message.data)
        break
      case 'activity':
        handleActivity(message.data)
        break
      default:
        logger.userAction('websocket_unknown_message_type', { type: message.type })
    }
  }

  const handlePatientStatusUpdate = async (data: any) => {
    logger.userAction('patient_status_update_received', { 
      patientId: data.patientId,
      newStatus: data.status 
    })

    // Update the patient in the store
    if (data.patient) {
      updatePatient(data.patient)
    } else {
      // Fetch updated patient data
      fetchPatients()
    }

    // Show notification
    toast.info(`Patient ${data.patientName} status changed to ${data.status}`)
  }

  const handleNewAlert = (data: any) => {
    logger.userAction('new_alert_received', { 
      alertId: data.id,
      type: data.type,
      priority: data.priority 
    })

    // Temporarily disable toast notifications to prevent memory issues
    // switch (data.priority) {
    //   case 'critical':
    //     toast.error(`Critical Alert: ${data.title}`)
    //     break
    //   case 'warning':
    //     toast.warning(`Warning: ${data.title}`)
    //     break
    //   default:
    //     toast.info(`Alert: ${data.title}`)
    // }

    // Refresh activities to show new alert
    fetchActivities()
  }

  const handleActivity = (data: any) => {
    logger.userAction('activity_received', { 
      activityId: data.id,
      type: data.type 
    })

    // Refresh activities and metrics
    fetchActivities()
    fetchMetrics()
  }

  const wsConnection = useWebSocket({
    onMessage: handleMessage,
    onConnect: () => {
      logger.userAction('websocket_provider_connected')
      // Disable toast to prevent memory issues
      // toast.success('Real-time updates connected')
      
      // Subscribe to default channels
      subscribeToAlerts()
    },
    onDisconnect: () => {
      logger.userAction('websocket_provider_disconnected')
      // Disable toast to prevent memory issues
      // toast.warning('Real-time updates disconnected')
    },
    onError: (error) => {
      logger.error('WebSocket error in provider', error)
    },
    autoConnect: false, // Disable auto-connect to prevent crash
  })

  const subscribeToPatientUpdates = (patientId: string) => {
    wsConnection.send({
      type: 'subscribe',
      data: {
        channel: 'patient_updates',
        patientId,
      },
      timestamp: new Date().toISOString(),
    } as any)
    
    logger.userAction('subscribed_to_patient_updates', { patientId })
  }

  const unsubscribeFromPatientUpdates = (patientId: string) => {
    wsConnection.send({
      type: 'unsubscribe',
      data: {
        channel: 'patient_updates',
        patientId,
      },
      timestamp: new Date().toISOString(),
    } as any)
    
    logger.userAction('unsubscribed_from_patient_updates', { patientId })
  }

  const subscribeToAlerts = () => {
    wsConnection.send({
      type: 'subscribe',
      data: {
        channel: 'alerts',
      },
      timestamp: new Date().toISOString(),
    } as any)
    
    logger.userAction('subscribed_to_alerts')
  }

  const unsubscribeFromAlerts = () => {
    wsConnection.send({
      type: 'unsubscribe',
      data: {
        channel: 'alerts',
      },
      timestamp: new Date().toISOString(),
    } as any)
    
    logger.userAction('unsubscribed_from_alerts')
  }

  // Clean up subscriptions on unmount
  useEffect(() => {
    return () => {
      if (wsConnection.isConnected) {
        unsubscribeFromAlerts()
      }
    }
  }, [wsConnection.isConnected])

  const value: WebSocketContextType = {
    ...wsConnection,
    subscribeToPatientUpdates,
    unsubscribeFromPatientUpdates,
    subscribeToAlerts,
    unsubscribeFromAlerts,
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}