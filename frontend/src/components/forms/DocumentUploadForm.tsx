import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { FileUpload, type UploadedFile } from './FileUpload'
import { documentUploadFormSchema, type DocumentUploadFormData } from '@/schemas/operations.schema'

export type { DocumentUploadFormData }

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
  const [files, setFiles] = useState<UploadedFile[]>(initialData?.files || [])
  const [fileError, setFileError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<DocumentUploadFormData>({
    resolver: zodResolver(documentUploadFormSchema),
    defaultValues: {
      doc_name: initialData?.doc_name || '',
      category: initialData?.category || '',
      version: initialData?.version || '1.0',
      description: initialData?.description || '',
      tags: initialData?.tags || '',
      file_url: initialData?.file_url || '',
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting
  const hasFiles = files.length > 0

  const onFormSubmit = async (data: DocumentUploadFormData) => {
    if (files.length === 0) {
      setFileError('At least one file is required')
      return
    }
    setFileError(null)
    await onSubmit({
      ...data,
      files,
    })
  }

  const handleFilesChange = (newFiles: UploadedFile[]) => {
    setFiles(newFiles)
    if (newFiles.length > 0) {
      setFileError(null)
    }
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Document Information"
        description="Enter details about the document"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Document Name" error={errors.doc_name?.message} required>
            <Input
              {...register('doc_name')}
              placeholder="Enter document name..."
              disabled={formIsLoading}
            />
          </FormField>

          <FormField label="Category" error={errors.category?.message} required>
            <Select
              {...register('category')}
              options={categoryOptions}
              disabled={formIsLoading}
            />
          </FormField>

          <FormField label="Version">
            <Input
              {...register('version')}
              placeholder="e.g., 1.0"
              disabled={formIsLoading}
            />
          </FormField>

          <FormField label="Tags" helperText="Comma-separated (e.g., safety, fleet, training)">
            <Input
              {...register('tags')}
              placeholder="safety, fleet, training"
              disabled={formIsLoading}
            />
          </FormField>
        </div>

        <FormField label="Description">
          <Textarea
            {...register('description')}
            placeholder="Provide a brief description of this document..."
            rows={3}
            disabled={formIsLoading}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Upload File"
        description="Select the document file to upload"
      >
        <FileUpload
          value={files}
          onChange={handleFilesChange}
          accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
          maxFiles={5}
          maxSize={25 * 1024 * 1024}
          uploadEndpoint="/api/documents/upload"
          disabled={formIsLoading}
          multiple
        />

        {fileError && (
          <p className="mt-2 text-sm text-red-600">{fileError}</p>
        )}
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={formIsLoading || !hasFiles}>
          {formIsLoading ? 'Uploading...' : initialData?.id ? 'Update Document' : 'Upload Document'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default DocumentUploadForm
