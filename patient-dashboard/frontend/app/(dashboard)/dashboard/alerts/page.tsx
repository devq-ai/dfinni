'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, XCircle, Clock, Bell } from "lucide-react";

interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'warning' | 'info';
  timestamp: string;
  status: 'active' | 'acknowledged' | 'resolved';
  patientName?: string;
}

const mockAlerts: Alert[] = [
  {
    id: '1',
    title: 'Critical Vital Signs',
    description: 'Patient heart rate exceeded threshold (>120 bpm)',
    severity: 'critical',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    status: 'active',
    patientName: 'John Doe'
  },
  {
    id: '2',
    title: 'Medication Due',
    description: 'Patient medication schedule alert - Insulin due',
    severity: 'warning',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    status: 'acknowledged',
    patientName: 'Jane Smith'
  },
  {
    id: '3',
    title: 'Lab Results Available',
    description: 'New lab results ready for review',
    severity: 'info',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    status: 'resolved',
    patientName: 'Robert Johnson'
  }
];

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>(mockAlerts);
  const [filter, setFilter] = useState<'all' | 'active' | 'acknowledged' | 'resolved'>('all');

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-5 w-5 text-cyber-neon-pink" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-cyber-laser-yellow" />;
      case 'info':
        return <Bell className="h-5 w-5 text-cyber-electric-cyan" />;
      default:
        return <AlertCircle className="h-5 w-5" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-cyber-neon-pink text-cyber-white';
      case 'warning':
        return 'bg-cyber-laser-yellow text-cyber-void-black';
      case 'info':
        return 'bg-cyber-electric-cyan text-cyber-void-black';
      default:
        return 'bg-cyber-gray text-cyber-white';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-cyber-neon-pink';
      case 'acknowledged':
        return 'text-cyber-laser-yellow';
      case 'resolved':
        return 'text-cyber-matrix-green';
      default:
        return 'text-cyber-white';
    }
  };

  const filteredAlerts = alerts.filter(alert => 
    filter === 'all' || alert.status === filter
  );

  const handleAcknowledge = (alertId: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, status: 'acknowledged' } : alert
    ));
  };

  const handleResolve = (alertId: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === alertId ? { ...alert, status: 'resolved' } : alert
    ));
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffMs = now.getTime() - alertTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins} minutes ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${Math.floor(diffHours / 24)} days ago`;
  };

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Alerts</h1>
          <p className="text-muted-foreground">Monitor and manage system alerts</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
            className={filter === 'all' ? 'bg-cyber-electric-cyan text-cyber-void-black' : 'dark:border-[#3e3e3e]'}
          >
            All ({alerts.length})
          </Button>
          <Button
            variant={filter === 'active' ? 'default' : 'outline'}
            onClick={() => setFilter('active')}
            className={filter === 'active' ? 'bg-cyber-electric-cyan text-cyber-void-black' : 'dark:border-[#3e3e3e]'}
          >
            Active ({alerts.filter(a => a.status === 'active').length})
          </Button>
          <Button
            variant={filter === 'acknowledged' ? 'default' : 'outline'}
            onClick={() => setFilter('acknowledged')}
            className={filter === 'acknowledged' ? 'bg-cyber-electric-cyan text-cyber-void-black' : 'dark:border-[#3e3e3e]'}
          >
            Acknowledged ({alerts.filter(a => a.status === 'acknowledged').length})
          </Button>
          <Button
            variant={filter === 'resolved' ? 'default' : 'outline'}
            onClick={() => setFilter('resolved')}
            className={filter === 'resolved' ? 'bg-cyber-electric-cyan text-cyber-void-black' : 'dark:border-[#3e3e3e]'}
          >
            Resolved ({alerts.filter(a => a.status === 'resolved').length})
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {filteredAlerts.map((alert) => (
          <Card key={alert.id} className="bg-card border-2 border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getSeverityIcon(alert.severity)}
                  <div>
                    <CardTitle className="text-lg">{alert.title}</CardTitle>
                    <CardDescription>{alert.description}</CardDescription>
                    {alert.patientName && (
                      <p className="text-sm text-muted-foreground mt-1">Patient: {alert.patientName}</p>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <Badge className={getSeverityColor(alert.severity)}>
                    {alert.severity.toUpperCase()}
                  </Badge>
                  <span className={`text-sm font-medium ${getStatusColor(alert.status)}`}>
                    {alert.status.charAt(0).toUpperCase() + alert.status.slice(1)}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center text-sm text-muted-foreground">
                  <Clock className="h-4 w-4 mr-1" />
                  {getTimeAgo(alert.timestamp)}
                </div>
                <div className="flex space-x-2">
                  {alert.status === 'active' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleAcknowledge(alert.id)}
                      className="dark:border-[#3e3e3e]"
                    >
                      Acknowledge
                    </Button>
                  )}
                  {(alert.status === 'active' || alert.status === 'acknowledged') && (
                    <Button
                      size="sm"
                      onClick={() => handleResolve(alert.id)}
                      className="bg-cyber-matrix-green text-cyber-void-black hover:bg-cyber-matrix-green/80"
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Resolve
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}