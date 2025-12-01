import { useEffect, useState, FormEvent, ChangeEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface AllocationFormData {
  courier_id: string
  building_id: string
  room_id: string
  bed_id: string
  start_date: string
  end_date?: string
  status: 'active' | 'pending' | 'ended'
  notes?: string
}

export interface AllocationFormProps {
  initialData?: Partial<AllocationFormData>
  onSubmit: (data: AllocationFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
  buildings?: Array<{ id: string; name: string }>
  rooms?: Array<{ id: string; name: string; building_id: string }>
  beds?: Array<{ id: string; name: string; room_id: string }>
}

const formatDateInput = (date: Date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const buildInitialFormData = (initialData?: Partial<AllocationFormData>): AllocationFormData => ({
  courier_id: initialData?.courier_id ?? '',
  building_id: initialData?.building_id ?? '',
  room_id: initialData?.room_id ?? '',
  bed_id: initialData?.bed_id ?? '',
  start_date: initialData?.start_date ?? formatDateInput(new Date()),
  end_date: initialData?.end_date,
  status: initialData?.status ?? 'pending',
  notes: initialData?.notes ?? '',
})

export const AllocationForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
  buildings = [],
  rooms = [],
  beds = [],
}: AllocationFormProps) => {
  const [formData, setFormData] = useState<AllocationFormData>(buildInitialFormData(initialData))
  const [errors, setErrors] = useState<Partial<Record<keyof AllocationFormData, string>>>({})
  const [submitError, setSubmitError] = useState<string | null>(null)

  useEffect(() => {
    setFormData(buildInitialFormData(initialData))
    setErrors({})
    setSubmitError(null)
  }, [initialData])

  // Filter rooms by selected building
  const filteredRooms = formData.building_id
    ? rooms.filter((room) => room.building_id === formData.building_id)
    : []

  // Filter beds by selected room
  const filteredBeds = formData.room_id
    ? beds.filter((bed) => bed.room_id === formData.room_id)
    : []

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof AllocationFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (!formData.building_id) {
      newErrors.building_id = 'Building is required'
    }

    if (!formData.room_id) {
      newErrors.room_id = 'Room is required'
    }

    if (!formData.bed_id) {
      newErrors.bed_id = 'Bed is required'
    }

    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required'
    }

    if (formData.status === 'ended' && !formData.end_date) {
      newErrors.end_date = 'End date is required when status is ended'
    }

    if (formData.start_date && formData.end_date) {
      const startDate = new Date(formData.start_date)
      const endDate = new Date(formData.end_date)
      if (endDate < startDate) {
        newErrors.end_date = 'End date cannot be before start date'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitError(null)

    if (isLoading || !validate()) {
      return
    }

    try {
      await onSubmit(formData)
    } catch (err) {
      console.error('Allocation submission failed', err)
      setSubmitError('Failed to save allocation. Please try again.')
    }
  }

  const handleChange = (field: keyof AllocationFormData, value: string) => {
    setFormData((prev) => {
      const updatedData = { ...prev, [field]: value }

      // Reset dependent fields when parent selection changes
      if (field === 'building_id') {
        updatedData.room_id = ''
        updatedData.bed_id = ''
      } else if (field === 'room_id') {
        updatedData.bed_id = ''
      }

      return updatedData
    })
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Allocation Information"
        description="Assign accommodation to a courier"
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
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'active', label: 'Active' },
                { value: 'ended', label: 'Ended' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Accommodation Details"
        description="Select building, room, and bed"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormField label="Building" required error={errors.building_id}>
            <Select
              value={formData.building_id}
              onChange={(e) => handleChange('building_id', e.target.value)}
              options={[
                { value: '', label: 'Select a building...' },
                ...buildings.map((b) => ({ value: b.id, label: b.name })),
              ]}
            />
          </FormField>

          <FormField label="Room" required error={errors.room_id}>
            <Select
              value={formData.room_id}
              onChange={(e) => handleChange('room_id', e.target.value)}
              options={[
                { value: '', label: formData.building_id ? 'Select a room...' : 'Select building first' },
                ...filteredRooms.map((r) => ({ value: r.id, label: r.name })),
              ]}
              disabled={!formData.building_id}
            />
          </FormField>

          <FormField label="Bed" required error={errors.bed_id}>
            <Select
              value={formData.bed_id}
              onChange={(e) => handleChange('bed_id', e.target.value)}
              options={[
                { value: '', label: formData.room_id ? 'Select a bed...' : 'Select room first' },
                ...filteredBeds.map((b) => ({ value: b.id, label: b.name })),
              ]}
              disabled={!formData.room_id}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Allocation Period"
        description="Set the allocation dates"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Start Date" required error={errors.start_date}>
            <Input
              type="date"
              value={formData.start_date}
              onChange={(e) => handleChange('start_date', e.target.value)}
            />
          </FormField>

          <FormField label="End Date" error={errors.end_date}>
            <Input
              type="date"
              value={formData.end_date}
              onChange={(e) => handleChange('end_date', e.target.value)}
              placeholder="Optional - leave empty for ongoing"
            />
          </FormField>

          <div className="md:col-span-2">
            <FormField label="Notes">
              <Textarea
                value={formData.notes ?? ''}
                onChange={(e: ChangeEvent<HTMLTextAreaElement>) => handleChange('notes', e.target.value)}
                placeholder="Any additional notes about this allocation..."
                rows={3}
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      {submitError && (
        <div className="p-3 rounded border border-red-200 bg-red-50 text-red-800">
          {submitError}
        </div>
      )}

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Allocation' : 'Update Allocation'}
        </Button>
      </FormActions>
    </Form>
  )
}
