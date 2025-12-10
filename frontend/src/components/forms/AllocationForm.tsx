import { useEffect, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { allocationFormSchema, type AllocationFormData } from '@/schemas/admin.schema'

export type { AllocationFormData }

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
  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AllocationFormData>({
    resolver: zodResolver(allocationFormSchema),
    defaultValues: {
      courier_id: initialData?.courier_id ?? '',
      building_id: initialData?.building_id ?? '',
      room_id: initialData?.room_id ?? '',
      bed_id: initialData?.bed_id ?? '',
      start_date: initialData?.start_date ?? formatDateInput(new Date()),
      end_date: initialData?.end_date,
      status: initialData?.status ?? 'pending',
      notes: initialData?.notes ?? '',
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting

  // Watch values for dependent selects
  const buildingId = watch('building_id')
  const roomId = watch('room_id')

  // Filter rooms by selected building
  const filteredRooms = useMemo(() =>
    buildingId ? rooms.filter((room) => room.building_id === buildingId) : [],
    [buildingId, rooms]
  )

  // Filter beds by selected room
  const filteredBeds = useMemo(() =>
    roomId ? beds.filter((bed) => bed.room_id === roomId) : [],
    [roomId, beds]
  )

  // Reset dependent fields when parent selection changes
  useEffect(() => {
    const subscription = watch((_value, { name }) => {
      if (name === 'building_id') {
        setValue('room_id', '')
        setValue('bed_id', '')
      } else if (name === 'room_id') {
        setValue('bed_id', '')
      }
    })
    return () => subscription.unsubscribe()
  }, [watch, setValue])

  // Reset form when initialData changes
  useEffect(() => {
    reset({
      courier_id: initialData?.courier_id ?? '',
      building_id: initialData?.building_id ?? '',
      room_id: initialData?.room_id ?? '',
      bed_id: initialData?.bed_id ?? '',
      start_date: initialData?.start_date ?? formatDateInput(new Date()),
      end_date: initialData?.end_date,
      status: initialData?.status ?? 'pending',
      notes: initialData?.notes ?? '',
    })
    setSubmitError(null)
  }, [initialData, reset])

  const onFormSubmit = async (data: AllocationFormData) => {
    setSubmitError(null)
    try {
      await onSubmit(data)
    } catch (err) {
      console.error('Allocation submission failed', err)
      setSubmitError('Failed to save allocation. Please try again.')
    }
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Allocation Information"
        description="Assign accommodation to a courier"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Courier" required error={errors.courier_id?.message}>
            <Select
              value={watch('courier_id')}
              onChange={(e) => setValue('courier_id', e.target.value, { shouldValidate: true })}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              {...register('status')}
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
          <FormField label="Building" required error={errors.building_id?.message}>
            <Select
              value={watch('building_id')}
              onChange={(e) => setValue('building_id', e.target.value, { shouldValidate: true })}
              options={[
                { value: '', label: 'Select a building...' },
                ...buildings.map((b) => ({ value: b.id, label: b.name })),
              ]}
            />
          </FormField>

          <FormField label="Room" required error={errors.room_id?.message}>
            <Select
              value={watch('room_id')}
              onChange={(e) => setValue('room_id', e.target.value, { shouldValidate: true })}
              options={[
                { value: '', label: buildingId ? 'Select a room...' : 'Select building first' },
                ...filteredRooms.map((r) => ({ value: r.id, label: r.name })),
              ]}
              disabled={!buildingId}
            />
          </FormField>

          <FormField label="Bed" required error={errors.bed_id?.message}>
            <Select
              value={watch('bed_id')}
              onChange={(e) => setValue('bed_id', e.target.value, { shouldValidate: true })}
              options={[
                { value: '', label: roomId ? 'Select a bed...' : 'Select room first' },
                ...filteredBeds.map((b) => ({ value: b.id, label: b.name })),
              ]}
              disabled={!roomId}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Allocation Period"
        description="Set the allocation dates"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Start Date" required error={errors.start_date?.message}>
            <Input
              type="date"
              {...register('start_date')}
            />
          </FormField>

          <FormField label="End Date" error={errors.end_date?.message}>
            <Input
              type="date"
              {...register('end_date')}
              placeholder="Optional - leave empty for ongoing"
            />
          </FormField>

          <div className="md:col-span-2">
            <FormField label="Notes">
              <Textarea
                {...register('notes')}
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
        <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={formIsLoading}>
          {formIsLoading ? 'Saving...' : mode === 'create' ? 'Create Allocation' : 'Update Allocation'}
        </Button>
      </FormActions>
    </Form>
  )
}
