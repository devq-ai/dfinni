import { PatientList } from '@/components/patients/patient-list'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

export default function PatientsPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Patients</h1>
          <p className="text-muted-foreground mt-1">Manage patient records and information</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Patient
        </Button>
      </div>
      
      <PatientList />
    </div>
  )
}