import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface RoomFormData {
  building_id: string
  room_number: string
  floor: number
  capacity: number
  current_occupancy: number
  type: 'single' | 'shared' | 'dormitory' | 'suite'
  status: 'available' | 'occupied' | 'maintenance' | 'reserved'
  monthly_rent?: number
  amenities?: string
  assigned_couriers?: string
  notes?: string
}

export interface RoomFormProps {
  initialData?: Partial<RoomFormData>
  onSubmit: (data: RoomFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  buildings?: Array<{ id: string; name: string }>
}

export const RoomForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  buildings = [],
}: RoomFormProps) => {
  const [formData, setFormData] = useState<RoomFormData>({
    building_id: initialData?.building_id || '',
    room_number: initialData?.room_number || '',
    floor: initialData?.floor || 1,
    capacity: initialData?.capacity || 1,
    current_occupancy: initialData?.current_occupancy || 0,
    type: initialData?.type || 'single',
    status: initialData?.status || 'available',
    monthly_rent: initialData?.monthly_rent || 0,
    amenities: initialData?.amenities || '',
    assigned_couriers: initialData?.assigned_couriers || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof RoomFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof RoomFormData, string>> = {}

    if (!formData.building_id) {
      newErrors.building_id = 'Building is required'
    }

    if (!formData.room_number.trim()) {
      newErrors.room_number = 'Room number is required'
    }

    if (formData.floor <= 0) {
      newErrors.floor = 'Floor must be at least 1'
    }

    if (formData.capacity <= 0) {
      newErrors.capacity = 'Capacity must be at least 1'
    }

    if (formData.current_occupancy < 0) {
      newErrors.current_occupancy = 'Current occupancy cannot be negative'
    }

    if (formData.current_occupancy > formData.capacity) {
      newErrors.current_occupancy = 'Current occupancy cannot exceed room capacity'
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

  const handleChange = (field: keyof RoomFormData, value: string | number) => {
    const updatedData = { ...formData, [field]: value }

    // Auto-update status based on occupancy
    if (field === 'current_occupancy' || field === 'capacity') {
      const occupancy = field === 'current_occupancy' ? value as number : formData.current_occupancy
      const capacity = field === 'capacity' ? value as number : formData.capacity

      if (occupancy === 0 && formData.status === 'occupied') {
        updatedData.status = 'available'
      } else if (occupancy > 0 && occupancy >= capacity && formData.status === 'available') {
        updatedData.status = 'occupied'
      }
    }

    setFormData(updatedData)
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Room Information"
        description="Enter room details and location"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Building" required error={errors.building_id}>
            <Select
              value={formData.building_id}
              onChange={(e) => handleChange('building_id', e.target.value)}
              options={[
                { value: '', label: 'Select a building...' },
                ...buildings.map((b) => ({ value: b.id, label: b.name })),
              ]}
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Room Number" required error={errors.room_number}>
            <Input
              value={formData.room_number}
              onChange={(e) => handleChange('room_number', e.target.value)}
              placeholder="101"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Floor" required error={errors.floor}>
            <Input
              type="number"
              value={formData.floor}
              onChange={(e) => handleChange('floor', parseInt(e.target.value))}
              placeholder="1"
            />
          </FormField>

          <FormField label="Room Type" required>
            <Select
              value={formData.type}
              onChange={(e) => handleChange('type', e.target.value)}
              options={[
                { value: 'single', label: 'Single' },
                { value: 'shared', label: 'Shared' },
                { value: 'dormitory', label: 'Dormitory' },
                { value: 'suite', label: 'Suite' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'available', label: 'Available' },
                { value: 'occupied', label: 'Occupied' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'reserved', label: 'Reserved' },
              ]}
            />
          </FormField>

          <FormField label="Monthly Rent">
            <Input
              type="number"
              step="0.01"
              value={formData.monthly_rent}
              onChange={(e) => handleChange('monthly_rent', parseFloat(e.target.value))}
              placeholder="1000.00"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Capacity & Occupancy"
        description="Room capacity and current occupancy"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Capacity" required error={errors.capacity}>
            <Input
              type="number"
              value={formData.capacity}
              onChange={(e) => handleChange('capacity', parseInt(e.target.value))}
              placeholder="2"
            />
          </FormField>

          <FormField label="Current Occupancy" required error={errors.current_occupancy}>
            <Input
              type="number"
              value={formData.current_occupancy}
              onChange={(e) => handleChange('current_occupancy', parseInt(e.target.value))}
              placeholder="0"
            />
          </FormField>

          <FormField
            label="Assigned Couriers"
            helperText="Comma-separated list of courier IDs or names"
          >
            <Input
              value={formData.assigned_couriers}
              onChange={(e) => handleChange('assigned_couriers', e.target.value)}
              placeholder="Courier1, Courier2"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Amenities & Details"
        description="Room amenities and additional information"
      >
        <FormField
          label="Amenities"
          helperText="Comma-separated list (e.g., WiFi, AC, Private Bathroom)"
        >
          <Input
            value={formData.amenities}
            onChange={(e) => handleChange('amenities', e.target.value)}
            placeholder="WiFi, AC, Private Bathroom"
          />
        </FormField>

        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes about this room..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Room' : 'Update Room'}
        </Button>
      </FormActions>
    </Form>
  )
}
