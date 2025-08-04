import { AlertList } from '@/components/alerts/alert-list'
import { Button } from '@/components/ui/button'
import { Download, Settings } from 'lucide-react'

export default function AlertsPage() {
  return (
    <div className="container mx-auto py-6 px-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Healthcare Alerts</h1>
          <p className="text-muted-foreground mt-1">Monitor and manage patient alerts</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="border-[#3e3e3e] hover:bg-[#141414]">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button>
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>
      
      <AlertList />
    </div>
  )
}