'use client'

import { useEffect } from 'react'
import { useAIStore, type AIInsight } from '@/stores/ai-store'
import { logger } from '@/lib/logfire'
import { 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb, 
  Activity,
  ChevronRight,
  Loader2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { formatDistanceToNow } from 'date-fns'

interface InsightsDashboardProps {
  className?: string
  patientId?: string
}

export function InsightsDashboard({ 
  className,
  patientId 
}: InsightsDashboardProps) {
  const { insights, isLoadingInsights, fetchInsights } = useAIStore()

  useEffect(() => {
    logger.componentMount('InsightsDashboard', { patientId })
    fetchInsights()
    
    return () => {
      logger.componentUnmount('InsightsDashboard')
    }
  }, [fetchInsights, patientId])

  const getInsightIcon = (type: AIInsight['type']) => {
    switch (type) {
      case 'trend':
        return <TrendingUp className="h-5 w-5" />
      case 'anomaly':
        return <AlertTriangle className="h-5 w-5" />
      case 'prediction':
        return <Activity className="h-5 w-5" />
      case 'recommendation':
        return <Lightbulb className="h-5 w-5" />
    }
  }

  const getInsightColor = (type: AIInsight['type']) => {
    switch (type) {
      case 'trend':
        return 'text-blue-500'
      case 'anomaly':
        return 'text-yellow-500'
      case 'prediction':
        return 'text-purple-500'
      case 'recommendation':
        return 'text-green-500'
    }
  }

  const getSeverityBadge = (severity: AIInsight['severity']) => {
    const colors = {
      low: 'bg-zinc-700 text-zinc-300',
      medium: 'bg-yellow-500/20 text-yellow-400',
      high: 'bg-red-500/20 text-red-400',
    }

    return (
      <span className={cn(
        "px-2 py-1 text-xs font-medium rounded-full",
        colors[severity]
      )}>
        {severity}
      </span>
    )
  }

  const filteredInsights = patientId 
    ? insights.filter(i => i.patientId === patientId)
    : insights

  if (isLoadingInsights) {
    return (
      <div className={cn(
        "flex items-center justify-center h-64 bg-zinc-900 border border-zinc-800 rounded-lg",
        className
      )}>
        <div className="text-center">
          <Loader2 className="h-8 w-8 text-zinc-600 animate-spin mx-auto mb-4" />
          <p className="text-sm text-zinc-500">Loading AI insights...</p>
        </div>
      </div>
    )
  }

  if (filteredInsights.length === 0) {
    return (
      <div className={cn(
        "flex items-center justify-center h-64 bg-zinc-900 border border-zinc-800 rounded-lg",
        className
      )}>
        <div className="text-center">
          <Activity className="h-8 w-8 text-zinc-600 mx-auto mb-4" />
          <p className="text-sm text-zinc-500">
            No AI insights available yet
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchInsights}
            className="mt-4"
          >
            Refresh Insights
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      "bg-zinc-950 border border-zinc-800 rounded-lg",
      className
    )}>
      {/* Header */}
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-zinc-100">
            AI Insights
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchInsights}
            disabled={isLoadingInsights}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Insights Grid */}
      <div className="p-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredInsights.map((insight) => (
          <div
            key={insight.id}
            className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className={cn(
                "flex items-center gap-2",
                getInsightColor(insight.type)
              )}>
                {getInsightIcon(insight.type)}
                <span className="text-sm font-medium capitalize">
                  {insight.type}
                </span>
              </div>
              {getSeverityBadge(insight.severity)}
            </div>

            <h4 className="text-sm font-semibold text-zinc-100 mb-2">
              {insight.title}
            </h4>

            <p className="text-xs text-zinc-400 mb-3 line-clamp-2">
              {insight.description}
            </p>

            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">
                {formatDistanceToNow(new Date(insight.createdAt), {
                  addSuffix: true
                })}
              </span>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  logger.userAction('view_insight_details', { 
                    insightId: insight.id,
                    type: insight.type 
                  })
                }}
                className="h-7 px-2"
              >
                View
                <ChevronRight className="h-3 w-3 ml-1" />
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-blue-500">
              {filteredInsights.filter(i => i.type === 'trend').length}
            </p>
            <p className="text-xs text-zinc-500">Trends</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-yellow-500">
              {filteredInsights.filter(i => i.type === 'anomaly').length}
            </p>
            <p className="text-xs text-zinc-500">Anomalies</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-purple-500">
              {filteredInsights.filter(i => i.type === 'prediction').length}
            </p>
            <p className="text-xs text-zinc-500">Predictions</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-500">
              {filteredInsights.filter(i => i.type === 'recommendation').length}
            </p>
            <p className="text-xs text-zinc-500">Recommendations</p>
          </div>
        </div>
      </div>
    </div>
  )
}