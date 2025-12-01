import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { ImageUpload, type UploadedFile } from './FileUpload'
import { type IncidentReportFormData } from './formConfigs'

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
  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    incident_type: initialData?.incident_type || '',
    severity: initialData?.severity || 'medium' as const,
    location: initialData?.location || '',
    description: initialData?.description || '',
    status: initialData?.status || 'open' as const,
    reported_by: initialData?.reported_by || '',
    evidence_urls: initialData?.evidence_urls || [],
  })
  const [evidencePhotos, setEvidencePhotos] = useState<UploadedFile[]>(
    initialData?.evidence_photos || []
  )
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!formData.title.trim()) newErrors.title = 'Title is required'
    if (!formData.incident_type) newErrors.incident_type = 'Incident type is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    await onSubmit({
      ...formData,
      evidence_photos: evidencePhotos,
    })
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'critical': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Incident Details"
        description="Provide basic information about the incident"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <FormField label="Incident Title" error={errors.title} required>
              <Input
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="Brief description of the incident..."
                disabled={isLoading}
              />
            </FormField>
          </div>

          <FormField label="Incident Type" error={errors.incident_type} required>
            <Select
              value={formData.incident_type}
              onChange={(e) => handleChange('incident_type', e.target.value)}
              options={incidentTypeOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Severity" required>
            <Select
              value={formData.severity}
              onChange={(e) => handleChange('severity', e.target.value)}
              options={severityOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Location">
            <Input
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="Where did the incident occur?"
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Reported By">
            <Input
              value={formData.reported_by}
              onChange={(e) => handleChange('reported_by', e.target.value)}
              placeholder="Name of reporter"
              disabled={isLoading}
            />
          </FormField>
        </div>

        {formData.severity && (
          <div className="mt-4">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(formData.severity)}`}>
              Severity: {formData.severity.charAt(0).toUpperCase() + formData.severity.slice(1)}
            </span>
          </div>
        )}
      </FormSection>

      <FormSection
        title="Description"
        description="Provide a detailed account of what happened"
      >
        <FormField label="Full Description" error={errors.description} required>
          <Textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Describe the incident in detail. Include timeline, circumstances, and any relevant information..."
            rows={5}
            disabled={isLoading}
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
          disabled={isLoading}
        />
      </FormSection>

      <FormSection
        title="Status"
        description="Current status of the incident"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Status">
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={statusOptions}
              disabled={isLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : initialData?.id ? 'Update Incident' : 'Report Incident'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default IncidentReportingForm
