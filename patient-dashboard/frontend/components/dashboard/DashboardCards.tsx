import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, AlertCircle, UserCheck, Activity, TrendingUp, TrendingDown } from "lucide-react"

interface DashboardStats {
  total_patients: number
  active_alerts: number
  recent_appointments: number
  pending_reviews: number
  patient_growth: number
  alert_change: number
  appointment_change: number
  review_change: number
}

interface DashboardCardsProps {
  stats: DashboardStats
}

export function DashboardCards({ stats }: DashboardCardsProps) {
  const formatChange = (value: number) => {
    if (!value || isNaN(value)) return "0%"
    const sign = value > 0 ? "+" : ""
    return `${sign}${value}%`
  }

  const cards = [
    {
      title: "Total Patients",
      value: stats.total_patients || 0,
      icon: Users,
      change: stats.patient_growth,
      description: "Total registered patients"
    },
    {
      title: "Active Alerts",
      value: stats.active_alerts || 0,
      icon: AlertCircle,
      change: stats.alert_change,
      description: "Unresolved patient alerts"
    },
    {
      title: "Recent Appointments",
      value: stats.recent_appointments || 0,
      icon: UserCheck,
      change: stats.appointment_change,
      description: "Appointments this week"
    },
    {
      title: "Pending Reviews",
      value: stats.pending_reviews || 0,
      icon: Activity,
      change: stats.review_change,
      description: "Cases awaiting review"
    }
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {card.title}
            </CardTitle>
            <card.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground">
              {card.description}
            </p>
            {card.change !== undefined && (
              <div className="flex items-center mt-2">
                {card.change > 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                ) : card.change < 0 ? (
                  <TrendingDown className="h-4 w-4 text-red-600 mr-1" />
                ) : null}
                <span className={`text-xs ${
                  card.change > 0 ? "text-green-600" : 
                  card.change < 0 ? "text-red-600" : 
                  "text-muted-foreground"
                }`}>
                  {formatChange(card.change)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}