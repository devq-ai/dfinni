import { InsuranceAlertDashboard } from '@/components/alerts/insurance-alert-dashboard'
import { AlertManagement } from '@/components/alerts/alert-management'

export default function AlertsPage() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-zinc-100">Alert Management</h1>
        <p className="text-sm text-zinc-400 mt-1">
          Monitor and manage all system alerts and notifications
        </p>
      </div>

      {/* Insurance Alerts Section */}
      <div>
        <h2 className="text-lg font-semibold text-zinc-100 mb-4">Insurance Alerts</h2>
        <InsuranceAlertDashboard />
      </div>

      {/* General Alert Management Section */}
      <div>
        <h2 className="text-lg font-semibold text-zinc-100 mb-4">System Alerts</h2>
        <AlertManagement />
      </div>
    </div>
  )
}