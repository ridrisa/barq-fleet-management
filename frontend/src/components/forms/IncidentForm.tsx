import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface IncidentFormData {
  courier_id: string
  vehicle_id?: string
  incident_type: 'accident' | 'theft' | 'damage' | 'violation' | 'other'
  severity: 'minor' | 'moderate' | 'major' | 'critical'
  date: string
  time?: string
  location: string
  description: string
  injuries?: string
  property_damage?: string
  police_report?: string
  witnesses?: string
  insurance_claim?: string
  resolution_status: 'reported' | 'investigating' | 'resolved' | 'closed'
  cost_estimate?: number
  notes?: string
}

export interface IncidentFormProps {
  initialData?: Partial<IncidentFormData>
  onSubmit: (data: IncidentFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
  vehicles?: Array<{ id: string; plate_number: string }>
}

export const IncidentForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
  vehicles = [],
}: IncidentFormProps) => {
  const [formData, setFormData] = useState<IncidentFormData>({
    courier_id: initialData?.courier_id || '',
    vehicle_id: initialData?.vehicle_id || '',
    incident_type: initialData?.incident_type || 'accident',
    severity: initialData?.severity || 'minor',
    date: initialData?.date || new Date().toISOString().split('T')[0],
    time: initialData?.time || '',
    location: initialData?.location || '',
    description: initialData?.description || '',
    injuries: initialData?.injuries || '',
    property_damage: initialData?.property_damage || '',
    police_report: initialData?.police_report || '',
    witnesses: initialData?.witnesses || '',
    insurance_claim: initialData?.insurance_claim || '',
    resolution_status: initialData?.resolution_status || 'reported',
    cost_estimate: initialData?.cost_estimate || 0,
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof IncidentFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof IncidentFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (!formData.date) {
      newErrors.date = 'Date is required'
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Location is required'
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    } else if (formData.description.trim().length < 20) {
      newErrors.description = 'Description must be at least 20 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    await onSubmit(formData)
  }

  const handleChange = (field: keyof IncidentFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Incident Information"
        description="Report an incident involving a courier or vehicle"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Courier" required error={errors.courier_id}>
            <Select
              value={formData.courier_id}
              onChange={(e) => handleChange('courier_id', e.target.value)}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Vehicle">
            <Select
              value={formData.vehicle_id}
              onChange={(e) => handleChange('vehicle_id', e.target.value)}
              options={[
                { value: '', label: 'No vehicle involved' },
                ...vehicles.map((v) => ({ value: v.id, label: v.plate_number })),
              ]}
            />
          </FormField>

          <FormField label="Incident Type" required>
            <Select
              value={formData.incident_type}
              onChange={(e) => handleChange('incident_type', e.target.value)}
              options={[
                { value: 'accident', label: 'Accident' },
                { value: 'theft', label: 'Theft' },
                { value: 'damage', label: 'Damage' },
                { value: 'violation', label: 'Violation' },
                { value: 'other', label: 'Other' },
              ]}
            />
          </FormField>

          <FormField label="Severity" required>
            <Select
              value={formData.severity}
              onChange={(e) => handleChange('severity', e.target.value)}
              options={[
                { value: 'minor', label: 'Minor' },
                { value: 'moderate', label: 'Moderate' },
                { value: 'major', label: 'Major' },
                { value: 'critical', label: 'Critical' },
              ]}
            />
          </FormField>

          <FormField label="Date" required error={errors.date}>
            <Input
              type="date"
              value={formData.date}
              onChange={(e) => handleChange('date', e.target.value)}
            />
          </FormField>

          <FormField label="Time">
            <Input
              type="time"
              value={formData.time}
              onChange={(e) => handleChange('time', e.target.value)}
            />
          </FormField>

          <FormField label="Location" required error={errors.location}>
            <Input
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="Incident location address"
            />
          </FormField>

          <FormField label="Resolution Status" required>
            <Select
              value={formData.resolution_status}
              onChange={(e) => handleChange('resolution_status', e.target.value)}
              options={[
                { value: 'reported', label: 'Reported' },
                { value: 'investigating', label: 'Investigating' },
                { value: 'resolved', label: 'Resolved' },
                { value: 'closed', label: 'Closed' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Incident Details"
        description="Detailed description of what happened"
      >
        <FormField label="Description" required error={errors.description}>
          <Input
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Provide a detailed description of the incident..."
          />
        </FormField>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Injuries (if any)">
            <Input
              value={formData.injuries}
              onChange={(e) => handleChange('injuries', e.target.value)}
              placeholder="Description of any injuries"
            />
          </FormField>

          <FormField label="Property Damage">
            <Input
              value={formData.property_damage}
              onChange={(e) => handleChange('property_damage', e.target.value)}
              placeholder="Description of property damage"
            />
          </FormField>

          <FormField label="Cost Estimate">
            <Input
              type="number"
              step="0.01"
              value={formData.cost_estimate}
              onChange={(e) => handleChange('cost_estimate', parseFloat(e.target.value))}
              placeholder="0.00"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Official Reports & Documentation"
        description="Police reports, insurance claims, and witness information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Police Report Number">
            <Input
              value={formData.police_report}
              onChange={(e) => handleChange('police_report', e.target.value)}
              placeholder="PR-123456"
            />
          </FormField>

          <FormField label="Insurance Claim Number">
            <Input
              value={formData.insurance_claim}
              onChange={(e) => handleChange('insurance_claim', e.target.value)}
              placeholder="IC-123456"
            />
          </FormField>

          <FormField label="Witnesses">
            <Input
              value={formData.witnesses}
              onChange={(e) => handleChange('witnesses', e.target.value)}
              placeholder="Names and contact information of witnesses"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and follow-up actions"
      >
        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes or follow-up actions..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Report Incident' : 'Update Incident'}
        </Button>
      </FormActions>
    </Form>
  )
}
