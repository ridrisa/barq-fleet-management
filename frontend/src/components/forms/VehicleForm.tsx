import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface VehicleFormData {
  plate_number: string
  type: 'sedan' | 'van' | 'truck' | 'motorcycle' | 'bicycle'
  make: string
  model: string
  year: number
  color?: string
  fuel_type: 'gasoline' | 'diesel' | 'electric' | 'hybrid'
  ownership: 'owned' | 'leased' | 'rented'
  status: 'available' | 'in_use' | 'maintenance' | 'retired'
  purchase_date?: string
  registration_expiry?: string
  insurance_expiry?: string
  last_maintenance?: string
  mileage?: number
  vin?: string
}

export interface VehicleFormProps {
  initialData?: Partial<VehicleFormData>
  onSubmit: (data: VehicleFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const VehicleForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: VehicleFormProps) => {
  const [formData, setFormData] = useState<VehicleFormData>({
    plate_number: initialData?.plate_number || '',
    type: initialData?.type || 'sedan',
    make: initialData?.make || '',
    model: initialData?.model || '',
    year: initialData?.year || new Date().getFullYear(),
    color: initialData?.color || '',
    fuel_type: initialData?.fuel_type || 'gasoline',
    ownership: initialData?.ownership || 'owned',
    status: initialData?.status || 'available',
    purchase_date: initialData?.purchase_date || '',
    registration_expiry: initialData?.registration_expiry || '',
    insurance_expiry: initialData?.insurance_expiry || '',
    last_maintenance: initialData?.last_maintenance || '',
    mileage: initialData?.mileage || 0,
    vin: initialData?.vin || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof VehicleFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof VehicleFormData, string>> = {}

    if (!formData.plate_number.trim()) {
      newErrors.plate_number = 'Plate number is required'
    }

    if (!formData.make.trim()) {
      newErrors.make = 'Make is required'
    }

    if (!formData.model.trim()) {
      newErrors.model = 'Model is required'
    }

    if (formData.year < 1900 || formData.year > new Date().getFullYear() + 1) {
      newErrors.year = 'Invalid year'
    }

    if (formData.registration_expiry) {
      const expiryDate = new Date(formData.registration_expiry)
      if (expiryDate < new Date()) {
        newErrors.registration_expiry = 'Registration has expired'
      }
    }

    if (formData.insurance_expiry) {
      const expiryDate = new Date(formData.insurance_expiry)
      if (expiryDate < new Date()) {
        newErrors.insurance_expiry = 'Insurance has expired'
      }
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

  const handleChange = (field: keyof VehicleFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Vehicle Information"
        description="Enter the vehicle's basic details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Plate Number" required error={errors.plate_number}>
            <Input
              value={formData.plate_number}
              onChange={(e) => handleChange('plate_number', e.target.value)}
              placeholder="ABC-1234"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Type" required>
            <Select
              value={formData.type}
              onChange={(e) => handleChange('type', e.target.value)}
              options={[
                { value: 'sedan', label: 'Sedan' },
                { value: 'van', label: 'Van' },
                { value: 'truck', label: 'Truck' },
                { value: 'motorcycle', label: 'Motorcycle' },
                { value: 'bicycle', label: 'Bicycle' },
              ]}
            />
          </FormField>

          <FormField label="Make" required error={errors.make}>
            <Input
              value={formData.make}
              onChange={(e) => handleChange('make', e.target.value)}
              placeholder="Toyota"
            />
          </FormField>

          <FormField label="Model" required error={errors.model}>
            <Input
              value={formData.model}
              onChange={(e) => handleChange('model', e.target.value)}
              placeholder="Camry"
            />
          </FormField>

          <FormField label="Year" required error={errors.year}>
            <Input
              type="number"
              value={formData.year}
              onChange={(e) => handleChange('year', parseInt(e.target.value))}
              placeholder="2023"
            />
          </FormField>

          <FormField label="Color">
            <Input
              value={formData.color}
              onChange={(e) => handleChange('color', e.target.value)}
              placeholder="White"
            />
          </FormField>

          <FormField label="VIN">
            <Input
              value={formData.vin}
              onChange={(e) => handleChange('vin', e.target.value)}
              placeholder="1HGBH41JXMN109186"
            />
          </FormField>

          <FormField label="Mileage">
            <Input
              type="number"
              value={formData.mileage}
              onChange={(e) => handleChange('mileage', parseInt(e.target.value))}
              placeholder="50000"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Operational Details"
        description="Fuel type, ownership, and status"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Fuel Type" required>
            <Select
              value={formData.fuel_type}
              onChange={(e) => handleChange('fuel_type', e.target.value)}
              options={[
                { value: 'gasoline', label: 'Gasoline' },
                { value: 'diesel', label: 'Diesel' },
                { value: 'electric', label: 'Electric' },
                { value: 'hybrid', label: 'Hybrid' },
              ]}
            />
          </FormField>

          <FormField label="Ownership" required>
            <Select
              value={formData.ownership}
              onChange={(e) => handleChange('ownership', e.target.value)}
              options={[
                { value: 'owned', label: 'Owned' },
                { value: 'leased', label: 'Leased' },
                { value: 'rented', label: 'Rented' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'available', label: 'Available' },
                { value: 'in_use', label: 'In Use' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'retired', label: 'Retired' },
              ]}
            />
          </FormField>

          <FormField label="Purchase Date">
            <Input
              type="date"
              value={formData.purchase_date}
              onChange={(e) => handleChange('purchase_date', e.target.value)}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Registration & Maintenance"
        description="Important dates and maintenance records"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Registration Expiry" error={errors.registration_expiry}>
            <Input
              type="date"
              value={formData.registration_expiry}
              onChange={(e) => handleChange('registration_expiry', e.target.value)}
            />
          </FormField>

          <FormField label="Insurance Expiry" error={errors.insurance_expiry}>
            <Input
              type="date"
              value={formData.insurance_expiry}
              onChange={(e) => handleChange('insurance_expiry', e.target.value)}
            />
          </FormField>

          <FormField label="Last Maintenance">
            <Input
              type="date"
              value={formData.last_maintenance}
              onChange={(e) => handleChange('last_maintenance', e.target.value)}
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Vehicle' : 'Update Vehicle'}
        </Button>
      </FormActions>
    </Form>
  )
}
