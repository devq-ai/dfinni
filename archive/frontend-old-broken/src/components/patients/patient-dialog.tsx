'use client'

import { useState, useEffect } from 'react'
import { usePatientStore } from '@/stores/patient-store'
import { logger } from '@/lib/logfire'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { CreatePatientData, PatientStatus, RiskLevel } from '@/types/patient'

interface PatientDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  mode: 'create' | 'edit'
}

export function PatientDialog({ open, onOpenChange, mode }: PatientDialogProps) {
  const { selectedPatient, createPatient, updatePatient } = usePatientStore()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState<CreatePatientData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    status: 'INQUIRY',
    risk_level: 'LOW',
  })

  useEffect(() => {
    if (mode === 'edit' && selectedPatient) {
      setFormData({
        first_name: selectedPatient.first_name,
        last_name: selectedPatient.last_name,
        email: selectedPatient.email,
        phone: selectedPatient.phone,
        date_of_birth: selectedPatient.date_of_birth,
        status: selectedPatient.status,
        risk_level: selectedPatient.risk_level,
      })
    } else {
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        date_of_birth: '',
        status: 'INQUIRY',
        risk_level: 'LOW',
      })
    }
    setError(null)
  }, [mode, selectedPatient, open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      if (mode === 'create') {
        await createPatient(formData)
        logger.userAction('patient_created', { email: formData.email })
      } else if (selectedPatient) {
        await updatePatient({ id: selectedPatient.id, ...formData })
        logger.userAction('patient_updated', { patientId: selectedPatient.id })
      }
      onOpenChange(false)
    } catch (error) {
      logger.error(`Failed to ${mode} patient`, error)
      setError(error instanceof Error ? error.message : `Failed to ${mode} patient`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (field: keyof CreatePatientData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-zinc-900 border-zinc-800">
        <DialogHeader>
          <DialogTitle className="text-zinc-100">
            {mode === 'create' ? 'Add New Patient' : 'Edit Patient'}
          </DialogTitle>
          <DialogDescription className="text-zinc-400">
            {mode === 'create' 
              ? 'Enter the patient details below.' 
              : 'Update the patient information below.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-500 text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="first_name" className="text-zinc-200">
                First Name
              </Label>
              <Input
                id="first_name"
                value={formData.first_name}
                onChange={(e) => handleInputChange('first_name', e.target.value)}
                required
                className="bg-zinc-950 border-zinc-800"
              />
            </div>

            <div>
              <Label htmlFor="last_name" className="text-zinc-200">
                Last Name
              </Label>
              <Input
                id="last_name"
                value={formData.last_name}
                onChange={(e) => handleInputChange('last_name', e.target.value)}
                required
                className="bg-zinc-950 border-zinc-800"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="email" className="text-zinc-200">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              required
              className="bg-zinc-950 border-zinc-800"
            />
          </div>

          <div>
            <Label htmlFor="phone" className="text-zinc-200">
              Phone
            </Label>
            <Input
              id="phone"
              type="tel"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              required
              className="bg-zinc-950 border-zinc-800"
            />
          </div>

          <div>
            <Label htmlFor="date_of_birth" className="text-zinc-200">
              Date of Birth
            </Label>
            <Input
              id="date_of_birth"
              type="date"
              value={formData.date_of_birth}
              onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
              required
              className="bg-zinc-950 border-zinc-800"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="status" className="text-zinc-200">
                Status
              </Label>
              <Select
                value={formData.status}
                onValueChange={(value) => handleInputChange('status', value as PatientStatus)}
              >
                <SelectTrigger id="status" className="bg-zinc-950 border-zinc-800">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  <SelectItem value="INQUIRY">Inquiry</SelectItem>
                  <SelectItem value="ONBOARDING">Onboarding</SelectItem>
                  <SelectItem value="ACTIVE">Active</SelectItem>
                  <SelectItem value="CHURNED">Churned</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="risk_level" className="text-zinc-200">
                Risk Level
              </Label>
              <Select
                value={formData.risk_level}
                onValueChange={(value) => handleInputChange('risk_level', value as RiskLevel)}
              >
                <SelectTrigger id="risk_level" className="bg-zinc-950 border-zinc-800">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-zinc-900 border-zinc-800">
                  <SelectItem value="LOW">Low Risk</SelectItem>
                  <SelectItem value="MEDIUM">Medium Risk</SelectItem>
                  <SelectItem value="HIGH">High Risk</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting 
                ? (mode === 'create' ? 'Creating...' : 'Updating...') 
                : (mode === 'create' ? 'Create Patient' : 'Update Patient')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}