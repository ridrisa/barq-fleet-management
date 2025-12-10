import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { ImageUpload, type UploadedFile } from './FileUpload'
import { incidentFormSchema, type IncidentReportFormData } from '@/schemas/operations.schema'

export type { IncidentReportFormData }

export interface IncidentReportingFormProps {
  initialData?: Partial<IncidentReportFormData & { evidence_photos?: UploadedFile[] }> & { id?: string }
  onSubmit: (data: IncidentReportFormData & { evidence_photos: UploadedFile[] }) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
}

const incidentTypeOptions = [
  { value: '', label: 'Select type...' },
  { value: 'accident', label: 'Accident' },
  { value: 'theft', label: 'Theft' },
  { value: 'damage', label: 'Property Damage' },
  { value: 'complaint', label: 'Customer Complaint' },
  { value: 'injury', label: 'Injury' },
  { value: 'other', label: 'Other' },
]

const severityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
]

const statusOptions = [
  { value: 'open', label: 'Open' },
  { value: 'investigating', label: 'Investigating' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
]

export const IncidentReportingForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false
}: IncidentReportingFormProps) => {
  const [evidencePhotos, setEvidencePhotos] = useState<UploadedFile[]>(
    initialData?.evidence_photos || []
  )

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<IncidentReportFormData>({
    resolver: zodResolver(incidentFormSchema),
    defaultValues: {
      title: initialData?.title || '',
      incident_type: initialData?.incident_type || '',
      severity: initialData?.severity || 'medium',
      location: initialData?.location || '',
      description: initialData?.description || '',
      status: initialData?.status || 'open',
      reported_by: initialData?.reported_by || '',
      evidence_urls: initialData?.evidence_urls || [],
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting
  const severity = watch('severity')

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'critical': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const onFormSubmit = async (data: IncidentReportFormData) => {
    await onSubmit({
      ...data,
      evidence_photos: evidencePhotos,
    })
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Incident Details"
        description="Provide basic information about the incident"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <FormField label="Incident Title" error={errors.title?.message} required>
              <Input
                {...register('title')}
                placeholder="Brief description of the incident..."
                disabled={formIsLoading}
              />
            </FormField>
          </div>

          <FormField label="Incident Type" error={errors.incident_type?.message} required>
            <Select
              {...register('incident_type')}
              options={incidentTypeOptions}
              disabled={formIsLoading}
            />
          </FormField>

          <FormField label="Severity" required>
            <Select
              {...register('severity')}
              options={severityOptions}
              disabled={formIsLoading}
            />
          </FormField>

          <FormField label="Location">
            <Input
              {...register('location')}
              placeholder="Where did the incident occur?"
              disabled={formIsLoading}
            />
          </FormField>

          <FormField label="Reported By">
            <Input
              {...register('reported_by')}
              placeholder="Name of reporter"
              disabled={formIsLoading}
            />
          </FormField>
        </div>

        {severity && (
          <div className="mt-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(severity)}`}>
              Severity: {severity.charAt(0).toUpperCase() + severity.slice(1)}
            </span>
          </div>
        )}
      </FormSection>

      <FormSection
        title="Description"
        description="Provide a detailed account of what happened"
      >
        <FormField label="Full Description" error={errors.description?.message} required>
          <Textarea
            {...register('description')}
            placeholder="Describe the incident in detail. Include timeline, circumstances, and any relevant information..."
            rows={5}
            disabled={formIsLoading}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Evidence Photos"
        description="Upload photos documenting the incident"
      >
        <ImageUpload
          value={evidencePhotos}
          onChange={setEvidencePhotos}
          maxFiles={10}
          maxSize={10 * 1024 * 1024}
          disabled={formIsLoading}
        />
      </FormSection>

      <FormSection
        title="Status"
        description="Current status of the incident"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Status">
            <Select
              {...register('status')}
              options={statusOptions}
              disabled={formIsLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={formIsLoading}>
          {formIsLoading ? 'Saving...' : initialData?.id ? 'Update Incident' : 'Report Incident'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default IncidentReportingForm
