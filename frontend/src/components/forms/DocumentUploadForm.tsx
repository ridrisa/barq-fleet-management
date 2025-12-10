import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { FileUpload, type UploadedFile } from './FileUpload'
import { type DocumentUploadFormData } from './formConfigs'

export interface DocumentUploadFormProps {
  initialData?: Partial<DocumentUploadFormData & { files?: UploadedFile[] }> & { id?: string }
  onSubmit: (data: DocumentUploadFormData & { files: UploadedFile[] }) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
}

const categoryOptions = [
  { value: '', label: 'Select category...' },
  { value: 'Procedures', label: 'Procedures' },
  { value: 'Policies', label: 'Policies' },
  { value: 'Training', label: 'Training Materials' },
  { value: 'Reports', label: 'Reports' },
  { value: 'Templates', label: 'Templates' },
  { value: 'Other', label: 'Other' },
]

export const DocumentUploadForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false
}: DocumentUploadFormProps) => {
  const [formData, setFormData] = useState({
    doc_name: initialData?.doc_name || '',
    category: initialData?.category || '',
    version: initialData?.version || '1.0',
    description: initialData?.description || '',
    tags: initialData?.tags || '',
  })
  const [files, setFiles] = useState<UploadedFile[]>(initialData?.files || [])
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!formData.doc_name.trim()) newErrors.doc_name = 'Document name is required'
    if (!formData.category) newErrors.category = 'Category is required'
    if (files.length === 0) newErrors.files = 'At least one file is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    await onSubmit({
      ...formData,
      file_url: '', // This will be set by the backend after upload
      files,
    })
  }

  const hasFiles = files.length > 0

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Document Information"
        description="Enter details about the document"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Document Name" error={errors.doc_name} required>
            <Input
              value={formData.doc_name}
              onChange={(e) => handleChange('doc_name', e.target.value)}
              placeholder="Enter document name..."
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Category" error={errors.category} required>
            <Select
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              options={categoryOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Version">
            <Input
              value={formData.version}
              onChange={(e) => handleChange('version', e.target.value)}
              placeholder="e.g., 1.0"
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Tags" helperText="Comma-separated (e.g., safety, fleet, training)">
            <Input
              value={formData.tags}
              onChange={(e) => handleChange('tags', e.target.value)}
              placeholder="safety, fleet, training"
              disabled={isLoading}
            />
          </FormField>
        </div>

        <FormField label="Description">
          <Textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Provide a brief description of this document..."
            rows={3}
            disabled={isLoading}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Upload File"
        description="Select the document file to upload"
      >
        <FileUpload
          value={files}
          onChange={setFiles}
          accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
          maxFiles={5}
          maxSize={25 * 1024 * 1024}
          uploadEndpoint="/api/documents/upload"
          disabled={isLoading}
          multiple
        />

        {errors.files && (
          <p className="mt-2 text-sm text-red-600">{errors.files}</p>
        )}
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading || !hasFiles}>
          {isLoading ? 'Uploading...' : initialData?.id ? 'Update Document' : 'Upload Document'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default DocumentUploadForm
