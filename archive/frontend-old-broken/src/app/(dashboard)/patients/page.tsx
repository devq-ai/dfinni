import { PatientDataTable } from '@/components/patients/data-table'
import { PatientStatusTracker } from '@/components/patients/patient-status-tracker'

export default function PatientsPage() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <PatientStatusTracker />
      <PatientDataTable />
    </div>
  )
}