'use client'

import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { useDashboardStore } from '@/stores/dashboard-store'
import { logger } from '@/lib/logfire'
import { Button } from '@/components/ui/Button'
import { 
  UserPlus, 
  Activity as ActivityIcon, 
  AlertTriangle, 
  TrendingUp,
  ChevronRight
} from 'lucide-react'
import type { Activity } from '@/types/dashboard'
import { cn } from '@/lib/utils'

export function ActivityFeed() {
  const { activities, isLoading, fetchActivities } = useDashboardStore()
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  const handleLoadMore = async () => {
    logger.userAction('load_more_activities', { currentPage: page })
    const nextPage = page + 1
    await fetchActivities(nextPage, 10)
    setPage(nextPage)
    
    // Check if we got fewer than expected items
    if (activities.length < nextPage * 10) {
      setHasMore(false)
    }
  }

  const handleActivityClick = (activity: Activity) => {
    logger.userAction('activity_click', { 
      activityId: activity.id,
      type: activity.type,
      patientId: activity.patientId 
    })
    // Navigation could be handled here
  }

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'patient_added':
        return <UserPlus className="h-5 w-5 text-green-500" />
      case 'status_changed':
        return <ActivityIcon className="h-5 w-5 text-blue-500" />
      case 'risk_updated':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'alert_created':
        return <TrendingUp className="h-5 w-5 text-red-500" />
      default:
        return <ActivityIcon className="h-5 w-5 text-zinc-400" />
    }
  }

  if (isLoading && activities.length === 0) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-zinc-100 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="flex items-start space-x-3">
                <div className="w-10 h-10 bg-zinc-800 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-zinc-800 rounded w-3/4" />
                  <div className="h-3 bg-zinc-800 rounded w-1/2" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-zinc-100">Recent Activity</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => logger.userAction('view_all_activities_click')}
        >
          View All
          <ChevronRight className="ml-1 h-4 w-4" />
        </Button>
      </div>

      <div className="space-y-4">
        {activities.length === 0 ? (
          <p className="text-zinc-400 text-sm text-center py-8">
            No recent activity to display
          </p>
        ) : (
          <>
            {activities.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start space-x-3 p-3 rounded-lg hover:bg-zinc-800/50 transition-colors cursor-pointer"
                onClick={() => handleActivityClick(activity)}
                role="button"
                tabIndex={0}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-zinc-100">
                    {activity.title}
                  </p>
                  <p className="text-sm text-zinc-400 mt-0.5">
                    {activity.description}
                  </p>
                  <p className="text-xs text-zinc-500 mt-1">
                    {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                  </p>
                </div>
              </div>
            ))}

            {hasMore && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleLoadMore}
                disabled={isLoading}
                className="w-full mt-4"
              >
                {isLoading ? 'Loading...' : 'Load More'}
              </Button>
            )}
          </>
        )}
      </div>
    </div>
  )
}