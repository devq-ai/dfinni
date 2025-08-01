'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Download, 
  FileText, 
  TrendingUp, 
  Users, 
  Activity,
  Calendar,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react'

export default function ReportsPage() {
  const [dateRange, setDateRange] = useState('last30days')
  
  // Mock data for charts
  const patientStats = [
    { month: 'Jan', active: 245, new: 23, discharged: 12 },
    { month: 'Feb', active: 258, new: 18, discharged: 5 },
    { month: 'Mar', active: 272, new: 25, discharged: 11 },
    { month: 'Apr', active: 285, new: 22, discharged: 9 },
    { month: 'May', active: 298, new: 20, discharged: 7 },
    { month: 'Jun', active: 312, new: 28, discharged: 14 }
  ]

  const riskDistribution = [
    { level: 'Low Risk', count: 120, percentage: 38 },
    { level: 'Medium Risk', count: 95, percentage: 30 },
    { level: 'High Risk', count: 65, percentage: 21 },
    { level: 'Critical', count: 32, percentage: 11 }
  ]

  const handleExport = (format: 'pdf' | 'csv') => {
    // TODO: Implement export functionality
    console.log(`Exporting as ${format}...`)
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Reports</h1>
          <p className="text-muted-foreground mt-1">Analytics and insights for your patient dashboard</p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={() => handleExport('csv')}
            variant="outline"
            className="border-[#3e3e3e] hover:bg-[#141414]"
          >
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button 
            onClick={() => handleExport('pdf')}
            className="bg-primary"
          >
            <FileText className="h-4 w-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">312</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-500">+8.2%</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Risk Score</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.4</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-yellow-500">+0.3</span> from last month
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-red-500">+15%</span> from last week
            </p>
          </CardContent>
        </Card>

        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <p className="text-xs text-muted-foreground">
              <span className="text-green-500">+2.1%</span> from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Report Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4 bg-[#141414] border border-[#3e3e3e]">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[#3e3e3e]">
            <BarChart3 className="h-4 w-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="patients" className="data-[state=active]:bg-[#3e3e3e]">
            <LineChart className="h-4 w-4 mr-2" />
            Patient Trends
          </TabsTrigger>
          <TabsTrigger value="risk" className="data-[state=active]:bg-[#3e3e3e]">
            <PieChart className="h-4 w-4 mr-2" />
            Risk Analysis
          </TabsTrigger>
          <TabsTrigger value="compliance" className="data-[state=active]:bg-[#3e3e3e]">
            <Activity className="h-4 w-4 mr-2" />
            Compliance
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-4">
            <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
              <CardHeader>
                <CardTitle>Monthly Patient Overview</CardTitle>
                <CardDescription>Active patients, new admissions, and discharges</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  {/* Placeholder for chart */}
                  <p>Chart visualization would go here (requires chart library integration)</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="patients">
          <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
            <CardHeader>
              <CardTitle>Patient Trends</CardTitle>
              <CardDescription>Patient population growth and retention metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  {patientStats.map((stat) => (
                    <div key={stat.month} className="space-y-2">
                      <h4 className="font-medium">{stat.month}</h4>
                      <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Active</span>
                          <span>{stat.active}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">New</span>
                          <span className="text-green-500">+{stat.new}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Discharged</span>
                          <span className="text-red-500">-{stat.discharged}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risk">
          <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Patient risk level breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {riskDistribution.map((risk) => (
                  <div key={risk.level} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{risk.level}</span>
                      <span className="font-medium">{risk.count} patients ({risk.percentage}%)</span>
                    </div>
                    <div className="w-full bg-[#0f0f0f] rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          risk.level === 'Low Risk' ? 'bg-green-500' :
                          risk.level === 'Medium Risk' ? 'bg-yellow-500' :
                          risk.level === 'High Risk' ? 'bg-orange-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${risk.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance">
          <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e]">
            <CardHeader>
              <CardTitle>Compliance Metrics</CardTitle>
              <CardDescription>Treatment adherence and follow-up compliance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-muted-foreground">Compliance metrics visualization coming soon...</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}