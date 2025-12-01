import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface BuildingFormData {
  name: string
  building_code: string
  address: string
  city: string
  country: string
  capacity: number
  floors: number
  total_rooms: number
  amenities?: string
  manager: string
  manager_contact: string
  status: 'active' | 'under_construction' | 'maintenance' | 'closed'
  construction_year?: number
  monthly_rent?: number
  notes?: string
}

export interface BuildingFormProps {
  initialData?: Partial<BuildingFormData>
  onSubmit: (data: BuildingFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const BuildingForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: BuildingFormProps) => {
  const [formData, setFormData] = useState<BuildingFormData>({
    name: initialData?.name || '',
    building_code: initialData?.building_code || '',
    address: initialData?.address || '',
    city: initialData?.city || '',
    country: initialData?.country || 'UAE',
    capacity: initialData?.capacity || 0,
    floors: initialData?.floors || 1,
    total_rooms: initialData?.total_rooms || 0,
    amenities: initialData?.amenities || '',
    manager: initialData?.manager || '',
    manager_contact: initialData?.manager_contact || '',
    status: initialData?.status || 'active',
    construction_year: initialData?.construction_year || new Date().getFullYear(),
    monthly_rent: initialData?.monthly_rent || 0,
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof BuildingFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof BuildingFormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Building name is required'
    }

    if (!formData.building_code.trim()) {
      newErrors.building_code = 'Building code is required'
    }

    if (!formData.address.trim()) {
      newErrors.address = 'Address is required'
    }

    if (!formData.city.trim()) {
      newErrors.city = 'City is required'
    }

    if (formData.capacity <= 0) {
      newErrors.capacity = 'Capacity must be greater than zero'
    }

    if (formData.floors <= 0) {
      newErrors.floors = 'Number of floors must be at least 1'
    }

    if (!formData.manager.trim()) {
      newErrors.manager = 'Manager name is required'
    }

    if (!formData.manager_contact.trim()) {
      newErrors.manager_contact = 'Manager contact is required'
    } else if (!/^\+?[\d\s-()]+$/.test(formData.manager_contact)) {
      newErrors.manager_contact = 'Invalid phone number format'
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

  const handleChange = (field: keyof BuildingFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Building Information"
        description="Enter building details and location"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Building Name" required error={errors.name}>
            <Input
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Main Staff Housing"
            />
          </FormField>

          <FormField label="Building Code" required error={errors.building_code}>
            <Input
              value={formData.building_code}
              onChange={(e) => handleChange('building_code', e.target.value)}
              placeholder="BLD-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'under_construction', label: 'Under Construction' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'closed', label: 'Closed' },
              ]}
            />
          </FormField>

          <FormField label="Construction Year">
            <Input
              type="number"
              value={formData.construction_year}
              onChange={(e) => handleChange('construction_year', parseInt(e.target.value))}
              placeholder="2020"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Location"
        description="Building address and location details"
      >
        <div className="grid grid-cols-1 gap-4">
          <FormField label="Address" required error={errors.address}>
            <Input
              value={formData.address}
              onChange={(e) => handleChange('address', e.target.value)}
              placeholder="123 Main Street"
            />
          </FormField>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="City" required error={errors.city}>
              <Input
                value={formData.city}
                onChange={(e) => handleChange('city', e.target.value)}
                placeholder="Dubai"
              />
            </FormField>

            <FormField label="Country" required>
              <Input
                value={formData.country}
                onChange={(e) => handleChange('country', e.target.value)}
                placeholder="UAE"
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      <FormSection
        title="Capacity & Layout"
        description="Building capacity and structure"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Total Capacity" required error={errors.capacity}>
            <Input
              type="number"
              value={formData.capacity}
              onChange={(e) => handleChange('capacity', parseInt(e.target.value))}
              placeholder="100"
            />
          </FormField>

          <FormField label="Number of Floors" required error={errors.floors}>
            <Input
              type="number"
              value={formData.floors}
              onChange={(e) => handleChange('floors', parseInt(e.target.value))}
              placeholder="5"
            />
          </FormField>

          <FormField label="Total Rooms">
            <Input
              type="number"
              value={formData.total_rooms}
              onChange={(e) => handleChange('total_rooms', parseInt(e.target.value))}
              placeholder="50"
            />
          </FormField>

          <FormField label="Monthly Rent">
            <Input
              type="number"
              step="0.01"
              value={formData.monthly_rent}
              onChange={(e) => handleChange('monthly_rent', parseFloat(e.target.value))}
              placeholder="50000.00"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Amenities & Management"
        description="Available amenities and manager information"
      >
        <FormField
          label="Amenities"
          helperText="Comma-separated list (e.g., WiFi, Parking, Gym)"
        >
          <Input
            value={formData.amenities}
            onChange={(e) => handleChange('amenities', e.target.value)}
            placeholder="WiFi, Parking, Gym, Laundry"
          />
        </FormField>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Building Manager" required error={errors.manager}>
            <Input
              value={formData.manager}
              onChange={(e) => handleChange('manager', e.target.value)}
              placeholder="Manager name"
            />
          </FormField>

          <FormField label="Manager Contact" required error={errors.manager_contact}>
            <Input
              type="tel"
              value={formData.manager_contact}
              onChange={(e) => handleChange('manager_contact', e.target.value)}
              placeholder="+971 50 123 4567"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and comments"
      >
        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes about this building..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Building' : 'Update Building'}
        </Button>
      </FormActions>
    </Form>
  )
}
