'use client'

import { Button } from '@/components/ui/Button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { X } from 'lucide-react'
import { logger } from '@/lib/logfire'
import type { PatientFilters as Filters, PatientStatus, RiskLevel } from '@/types/patient'

interface PatientFiltersProps {
  filters: Filters
  onFiltersChange: (filters: Filters) => void
  onClose: () => void
}

export function PatientFilters({ filters, onFiltersChange, onClose }: PatientFiltersProps) {
  const handleStatusChange = (value: string) => {
    logger.userAction('filter_by_status', { status: value })
    onFiltersChange({ ...filters, status: value as PatientStatus | 'ALL' })
  }

  const handleRiskLevelChange = (value: string) => {
    logger.userAction('filter_by_risk_level', { riskLevel: value })
    onFiltersChange({ ...filters, risk_level: value as RiskLevel | 'ALL' })
  }

  const handleClearFilters = () => {
    logger.userAction('clear_filters')
    onFiltersChange({})
    onClose()
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-zinc-100">Filters</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-8 w-8 p-0"
          aria-label="Close filters"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-1">
            Status
          </label>
          <Select
            value={filters.status || 'ALL'}
            onValueChange={handleStatusChange}
          >
            <SelectTrigger className="bg-zinc-950 border-zinc-800">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-800">
              <SelectItem value="ALL">All Statuses</SelectItem>
              <SelectItem value="INQUIRY">Inquiry</SelectItem>
              <SelectItem value="ONBOARDING">Onboarding</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="CHURNED">Churned</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium text-zinc-400 mb-1">
            Risk Level
          </label>
          <Select
            value={filters.risk_level || 'ALL'}
            onValueChange={handleRiskLevelChange}
          >
            <SelectTrigger className="bg-zinc-950 border-zinc-800">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-zinc-900 border-zinc-800">
              <SelectItem value="ALL">All Risk Levels</SelectItem>
              <SelectItem value="LOW">Low Risk</SelectItem>
              <SelectItem value="MEDIUM">Medium Risk</SelectItem>
              <SelectItem value="HIGH">High Risk</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex items-center justify-end space-x-2 mt-4">
        <Button
          variant="outline"
          size="sm"
          onClick={handleClearFilters}
        >
          Clear Filters
        </Button>
      </div>
    </div>
  )
}