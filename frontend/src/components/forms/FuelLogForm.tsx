import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface FuelLogFormData {
  vehicle_id: number | string
  date: string
  fuel_type: 'petrol' | 'diesel' | 'electric'
  liters: number | string
  cost: number | string
  odometer: number | string
  station?: string
  notes?: string
}

export interface FuelLogFormProps {
  initialData?: Partial<FuelLogFormData>
  onSubmit: (data: FuelLogFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  vehicles?: Array<{ id: number; plate_number: string }>
}

export const FuelLogForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  vehicles = [],
}: FuelLogFormProps) => {
  const [formData, setFormData] = useState<FuelLogFormData>({
    vehicle_id: initialData?.vehicle_id || '',
    date: initialData?.date || new Date().toISOString().split('T')[0],
    fuel_type: initialData?.fuel_type || 'petrol',
    liters: initialData?.liters || '',
    cost: initialData?.cost || '',
    odometer: initialData?.odometer || '',
    station: initialData?.station || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof FuelLogFormData, string>>>({})

  // Basic validation
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof FuelLogFormData, string>> = {}

    if (!formData.vehicle_id) {
      newErrors.vehicle_id = 'Vehicle is required'
    }

    if (!formData.date) {
      newErrors.date = 'Date is required'
    }

    if (!formData.liters) {
      newErrors.liters = 'Liters is required'
    } else if (Number(formData.liters) <= 0) {
      newErrors.liters = 'Liters must be greater than 0'
    }

    if (!formData.cost) {
      newErrors.cost = 'Cost is required'
    } else if (Number(formData.cost) <= 0) {
      newErrors.cost = 'Cost must be greater than 0'
    }

    if (!formData.odometer) {
      newErrors.odometer = 'Odometer reading is required'
    } else if (Number(formData.odometer) <= 0) {
      newErrors.odometer = 'Odometer reading must be greater than 0'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    // Convert string values to numbers
    const submitData = {
      ...formData,
      vehicle_id: Number(formData.vehicle_id),
      liters: Number(formData.liters),
      cost: Number(formData.cost),
      odometer: Number(formData.odometer),
    }

    await onSubmit(submitData)
  }

  const handleChange = (field: keyof FuelLogFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Fuel Log Details"
        description="Enter fuel consumption information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Vehicle" required error={errors.vehicle_id}>
            <Select
              value={String(formData.vehicle_id)}
              onChange={(e) => handleChange('vehicle_id', e.target.value)}
              options={[
                { value: '', label: 'Select Vehicle' },
                ...vehicles.map((v) => ({
                  value: String(v.id),
                  label: v.plate_number,
                })),
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

          <FormField label="Fuel Type" required>
            <Select
              value={formData.fuel_type}
              onChange={(e) => handleChange('fuel_type', e.target.value)}
              options={[
                { value: 'petrol', label: 'Petrol' },
                { value: 'diesel', label: 'Diesel' },
                { value: 'electric', label: 'Electric' },
              ]}
            />
          </FormField>

          <FormField label="Liters" required error={errors.liters}>
            <Input
              type="number"
              step="0.01"
              value={formData.liters}
              onChange={(e) => handleChange('liters', e.target.value)}
              placeholder="45.5"
            />
          </FormField>

          <FormField label="Cost (SAR)" required error={errors.cost}>
            <Input
              type="number"
              step="0.01"
              value={formData.cost}
              onChange={(e) => handleChange('cost', e.target.value)}
              placeholder="180.00"
            />
          </FormField>

          <FormField label="Odometer (km)" required error={errors.odometer}>
            <Input
              type="number"
              value={formData.odometer}
              onChange={(e) => handleChange('odometer', e.target.value)}
              placeholder="45250"
            />
          </FormField>

          <FormField label="Station">
            <Input
              value={formData.station}
              onChange={(e) => handleChange('station', e.target.value)}
              placeholder="ADNOC Station, Dubai"
            />
          </FormField>

          <FormField label="Notes">
            <Input
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Additional notes"
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Add Fuel Log' : 'Update Fuel Log'}
        </Button>
      </FormActions>
    </Form>
  )
}
