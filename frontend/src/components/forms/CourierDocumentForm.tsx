import { useState } from 'react'
import { DynamicForm } from './DynamicForm'
import { FileUpload, type UploadedFile } from './FileUpload'
import { FormSection } from './Form'
import {
  courierDocumentFormConfig,
  courierDocumentInitialData,
  courierDocumentFormSchema,
  getCourierOptions,
  type CourierDocumentFormData
} from './formConfigs'

export interface CourierDocumentFormProps {
  initialData?: Partial<CourierDocumentFormData & { files?: UploadedFile[] }> & { id?: string }
  onSubmit: (data: CourierDocumentFormData & { files: UploadedFile[] }) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: string; name: string }>
}

export const CourierDocumentForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = []
}: CourierDocumentFormProps) => {
  const [files, setFiles] = useState<UploadedFile[]>(initialData?.files || [])

  // Update config with courier options
  const config = {
    ...courierDocumentFormConfig,
    sections: courierDocumentFormConfig.sections.map(section => ({
      ...section,
      fields: section.fields.map(field => {
        if (field.name === 'courier_id') {
          return {
            ...field,
            options: getCourierOptions(couriers)
          }
        }
        return field
      })
    }))
  }

  const defaultValues = {
    ...courierDocumentInitialData,
    ...initialData
  }

  const handleSubmit = async (data: CourierDocumentFormData) => {
    await onSubmit({ ...data, files })
  }

  return (
    <div className="space-y-6">
      <DynamicForm
        formConfig={config}
        initialData={defaultValues}
        zodSchema={courierDocumentFormSchema}
        onSubmit={handleSubmit}
        onCancel={onCancel}
        isLoading={isLoading}
        submitButtonText={initialData?.id ? 'Update Document' : 'Upload Document'}
        renderBeforeActions={
          <FormSection title="Document File" description="Upload the document file">
            <FileUpload
              value={files}
              onChange={setFiles}
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              maxFiles={1}
              maxSize={10 * 1024 * 1024}
              uploadEndpoint="/api/documents/upload"
              disabled={isLoading}
            />
          </FormSection>
        }
      />
    </div>
  )
}

export default CourierDocumentForm
