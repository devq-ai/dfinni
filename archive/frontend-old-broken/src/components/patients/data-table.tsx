'use client'

import { useState } from 'react'
import { usePatientStore } from '@/stores/patient-store'
import { logger } from '@/lib/logfire'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { 
  ChevronDown, 
  ChevronUp, 
  Edit, 
  Trash2, 
  MoreHorizontal,
  Plus,
  Search,
  Filter
} from 'lucide-react'
import { PatientStatusBadge } from './patient-status-badge'
import { RiskLevelBadge } from './risk-level-badge'
import { PatientDialog } from './patient-dialog'
import { PatientFilters } from './patient-filters'
import { formatDate } from '@/lib/utils'
import type { Patient, PatientSortConfig } from '@/types/patient'

export function PatientDataTable() {
  const {
    patients,
    isLoading,
    error,
    filters,
    sortConfig,
    totalCount,
    currentPage,
    pageSize,
    fetchPatients,
    deletePatient,
    selectPatient,
    setFilters,
    setSortConfig,
    setPage,
  } = usePatientStore()

  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showEditDialog, setShowEditDialog] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [searchTerm, setSearchTerm] = useState(filters.search || '')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

  const handleSort = (key: keyof Patient) => {
    logger.userAction('sort_patients', { key })
    const newDirection = sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    setSortConfig({ key, direction: newDirection })
  }

  const handleSearch = () => {
    logger.userAction('search_patients', { searchTerm })
    setFilters({ ...filters, search: searchTerm })
  }

  const handleEdit = (patient: Patient) => {
    logger.userAction('edit_patient_start', { patientId: patient.id })
    selectPatient(patient)
    setShowEditDialog(true)
  }

  const handleDelete = async (id: string) => {
    if (deleteConfirmId === id) {
      try {
        await deletePatient(id)
        setDeleteConfirmId(null)
      } catch (error) {
        logger.error('Failed to delete patient', error, { patientId: id })
      }
    } else {
      setDeleteConfirmId(id)
      setTimeout(() => setDeleteConfirmId(null), 3000) // Reset after 3 seconds
    }
  }

  const totalPages = Math.ceil(totalCount / pageSize)

  const SortIcon = ({ column }: { column: keyof Patient }) => {
    if (sortConfig.key !== column) return null
    return sortConfig.direction === 'asc' ? 
      <ChevronUp className="ml-1 h-4 w-4" /> : 
      <ChevronDown className="ml-1 h-4 w-4" />
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold text-zinc-100">Patients</h2>
          <span className="text-sm text-zinc-400">
            {totalCount} total
          </span>
        </div>
        <Button 
          onClick={() => setShowCreateDialog(true)}
          className="flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Add Patient</span>
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 flex items-center space-x-2">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
            <Input
              placeholder="Search patients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>
          <Button 
            variant="outline" 
            onClick={handleSearch}
          >
            Search
          </Button>
        </div>
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center space-x-2"
        >
          <Filter className="h-4 w-4" />
          <span>Filters</span>
        </Button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <PatientFilters 
          filters={filters}
          onFiltersChange={setFilters}
          onClose={() => setShowFilters(false)}
        />
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-500">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="border border-zinc-800 rounded-lg overflow-hidden">
        <Table>
          <TableHeader className="bg-zinc-900">
            <TableRow className="border-zinc-800">
              <TableHead 
                className="cursor-pointer hover:bg-zinc-800"
                onClick={() => handleSort('last_name')}
              >
                <div className="flex items-center">
                  Name
                  <SortIcon column="last_name" />
                </div>
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-zinc-800"
                onClick={() => handleSort('email')}
              >
                <div className="flex items-center">
                  Email
                  <SortIcon column="email" />
                </div>
              </TableHead>
              <TableHead>Phone</TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-zinc-800"
                onClick={() => handleSort('status')}
              >
                <div className="flex items-center">
                  Status
                  <SortIcon column="status" />
                </div>
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-zinc-800"
                onClick={() => handleSort('risk_level')}
              >
                <div className="flex items-center">
                  Risk Level
                  <SortIcon column="risk_level" />
                </div>
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-zinc-800"
                onClick={() => handleSort('created_at')}
              >
                <div className="flex items-center">
                  Created
                  <SortIcon column="created_at" />
                </div>
              </TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-zinc-400">
                  Loading patients...
                </TableCell>
              </TableRow>
            ) : patients.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-zinc-400">
                  No patients found
                </TableCell>
              </TableRow>
            ) : (
              patients.map((patient) => (
                <TableRow key={patient.id} className="border-zinc-800 hover:bg-zinc-900/50">
                  <TableCell className="font-medium">
                    {patient.last_name}, {patient.first_name}
                  </TableCell>
                  <TableCell className="text-zinc-400">{patient.email}</TableCell>
                  <TableCell className="text-zinc-400">{patient.phone}</TableCell>
                  <TableCell>
                    <PatientStatusBadge status={patient.status} />
                  </TableCell>
                  <TableCell>
                    <RiskLevelBadge level={patient.risk_level} />
                  </TableCell>
                  <TableCell className="text-zinc-400">
                    {formatDate(patient.created_at)}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="bg-zinc-900 border-zinc-800">
                        <DropdownMenuItem
                          onClick={() => handleEdit(patient)}
                          className="cursor-pointer hover:bg-zinc-800"
                        >
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleDelete(patient.id)}
                          className="cursor-pointer hover:bg-zinc-800 text-red-500 hover:text-red-400"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          {deleteConfirmId === patient.id ? 'Click to confirm' : 'Delete'}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-zinc-400">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} patients
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + 1
                return (
                  <Button
                    key={page}
                    variant={page === currentPage ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setPage(page)}
                    className="w-8"
                  >
                    {page}
                  </Button>
                )
              })}
              {totalPages > 5 && <span className="text-zinc-400">...</span>}
              {totalPages > 5 && (
                <Button
                  variant={totalPages === currentPage ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPage(totalPages)}
                  className="w-8"
                >
                  {totalPages}
                </Button>
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Dialogs */}
      <PatientDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        mode="create"
      />
      <PatientDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        mode="edit"
      />
    </div>
  )
}