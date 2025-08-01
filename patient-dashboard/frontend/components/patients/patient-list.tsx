'use client'

import { useState, useEffect } from 'react'
import { Patient } from '@/types/patient'
import { patientsApi } from '@/lib/api/patients'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export function PatientList() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 10

  useEffect(() => {
    loadPatients()
  }, [page])

  const loadPatients = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await patientsApi.getPatients(page, pageSize)
      setPatients(response.patients)
      setTotal(response.total)
    } catch (err) {
      setError('Failed to load patients')
      console.error('Error loading patients:', err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskBadgeVariant = (score?: number): "default" | "secondary" | "destructive" | "outline" => {
    if (!score) return 'default'
    if (score <= 2) return 'secondary'
    if (score <= 4) return 'outline'
    return 'destructive'
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-muted-foreground">Loading patients...</div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e] p-4">
        <p className="text-destructive">{error}</p>
        <Button
          onClick={loadPatients}
          variant="outline"
          size="sm"
          className="mt-2 border-[#3e3e3e]"
        >
          Try again
        </Button>
      </Card>
    )
  }

  return (
    <div>
      <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e] overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-[#0f0f0f] border-b border-[#3e3e3e]">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Patient
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                MRN
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Risk Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Last Visit
              </th>
              <th className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#3e3e3e]">
            {patients.map((patient) => (
              <tr key={patient.id} className="hover:bg-[#0f0f0f] transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium">
                      {patient.firstName} {patient.lastName}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      DOB: {new Date(patient.dateOfBirth).toLocaleDateString()}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm">{patient.mrn}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm">{patient.email}</div>
                    <div className="text-sm text-muted-foreground">{patient.phone}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {patient.riskScore && (
                    <Badge variant={getRiskBadgeVariant(patient.riskScore)}>
                      {patient.riskScore}
                    </Badge>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Badge variant={patient.status === 'active' ? 'secondary' : 'outline'}>
                    {patient.status}
                  </Badge>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                  {patient.lastVisit 
                    ? new Date(patient.lastVisit).toLocaleDateString()
                    : 'N/A'
                  }
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Link
                    href={`/patients/${patient.id}`}
                    className="text-primary hover:text-primary/80 transition-colors"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {/* Pagination */}
      {total > pageSize && (
        <Card className="bg-card border-border dark:bg-[#141414] dark:border-[#3e3e3e] px-4 py-3 mt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">
                Showing{' '}
                <span className="font-medium">{(page - 1) * pageSize + 1}</span>
                {' '}to{' '}
                <span className="font-medium">
                  {Math.min(page * pageSize, total)}
                </span>
                {' '}of{' '}
                <span className="font-medium">{total}</span>
                {' '}results
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                variant="outline"
                size="sm"
                className="border-[#3e3e3e]"
              >
                Previous
              </Button>
              <Button
                onClick={() => setPage(page + 1)}
                disabled={page * pageSize >= total}
                variant="outline"
                size="sm"
                className="border-[#3e3e3e]"
              >
                Next
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}