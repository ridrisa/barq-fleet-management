import { useState, useRef, useCallback } from 'react'
import { Upload, X, File, Image, FileText, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

export interface UploadedFile {
  id: string
  name: string
  size: number
  type: string
  url: string
  uploadedAt: Date
}

export interface FileUploadProps {
  value: UploadedFile[]
  onChange: (files: UploadedFile[]) => void
  accept?: string
  maxFiles?: number
  maxSize?: number // in bytes
  uploadEndpoint?: string
  multiple?: boolean
  className?: string
  disabled?: boolean
}

export const FileUpload = ({
  value = [],
  onChange,
  accept = '*/*',
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB default
  uploadEndpoint = '/upload',
  multiple = true,
  className,
  disabled = false,
}: FileUploadProps) => {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="w-8 h-8 text-blue-500" />
    if (type.includes('pdf')) return <FileText className="w-8 h-8 text-red-500" />
    return <File className="w-8 h-8 text-gray-500" />
  }

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize) {
      return `File "${file.name}" exceeds maximum size of ${formatFileSize(maxSize)}`
    }

    if (accept !== '*/*') {
      const acceptedTypes = accept.split(',').map(t => t.trim())
      const isAccepted = acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return file.name.toLowerCase().endsWith(type.toLowerCase())
        }
        if (type.endsWith('/*')) {
          return file.type.startsWith(type.replace('/*', '/'))
        }
        return file.type === type
      })

      if (!isAccepted) {
        return `File "${file.name}" is not an accepted file type`
      }
    }

    return null
  }

  const uploadFile = async (file: File): Promise<UploadedFile | null> => {
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return null
    }

    try {
      const formData = new FormData()
      formData.append('file', file)

      const { data } = await api.post(uploadEndpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      return {
        id: data.id || Date.now().toString(),
        name: file.name,
        size: file.size,
        type: file.type,
        url: data.url || data.file_url || URL.createObjectURL(file),
        uploadedAt: new Date(),
      }
    } catch (err) {
      console.error('Upload failed:', err)
      setError(`Failed to upload "${file.name}"`)
      return null
    }
  }

  const handleFiles = useCallback(async (files: FileList | File[]) => {
    if (disabled) return

    const fileArray = Array.from(files)

    // Check max files limit
    if (value.length + fileArray.length > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed`)
      return
    }

    setError(null)
    setUploading(true)

    try {
      const uploadPromises = fileArray.map(file => uploadFile(file))
      const results = await Promise.all(uploadPromises)
      const successfulUploads = results.filter((f): f is UploadedFile => f !== null)

      if (successfulUploads.length > 0) {
        onChange([...value, ...successfulUploads])
      }
    } finally {
      setUploading(false)
    }
  }, [disabled, maxFiles, onChange, value])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) setIsDragging(true)
  }, [disabled])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files)
    }
  }, [handleFiles])

  const handleClick = () => {
    if (!disabled) fileInputRef.current?.click()
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files)
    }
    // Reset input so same file can be selected again
    e.target.value = ''
  }

  const handleRemove = (id: string) => {
    onChange(value.filter(file => file.id !== id))
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400',
          disabled && 'opacity-50 cursor-not-allowed',
          uploading && 'pointer-events-none'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
          className="hidden"
          disabled={disabled}
        />

        {uploading ? (
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
            <p className="text-gray-600">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <Upload className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-2">
              <span className="font-medium text-blue-600">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">
              {accept !== '*/*' ? `Accepted: ${accept}` : 'Any file type'} (max {formatFileSize(maxSize)})
            </p>
            {maxFiles > 1 && (
              <p className="text-xs text-gray-500 mt-1">
                {value.length} / {maxFiles} files uploaded
              </p>
            )}
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* File list */}
      {value.length > 0 && (
        <div className="space-y-2">
          {value.map(file => (
            <div
              key={file.id}
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              {getFileIcon(file.type)}

              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(file.size)}
                </p>
              </div>

              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => handleRemove(file.id)}
                disabled={disabled}
              >
                <X className="w-4 h-4 text-gray-500 hover:text-red-500" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Simplified single file upload
export const SingleFileUpload = (props: Omit<FileUploadProps, 'multiple' | 'maxFiles'>) => {
  return <FileUpload {...props} multiple={false} maxFiles={1} />
}

// Image-only upload with preview
export const ImageUpload = ({
  value,
  onChange,
  ...props
}: Omit<FileUploadProps, 'accept'>) => {
  return (
    <div className="space-y-4">
      <FileUpload
        {...props}
        value={value}
        onChange={onChange}
        accept="image/*"
      />

      {/* Image previews */}
      {value.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {value.map(file => (
            <div key={file.id} className="relative aspect-square">
              <img
                src={file.url}
                alt={file.name}
                className="w-full h-full object-cover rounded-lg"
              />
              <button
                type="button"
                onClick={() => onChange(value.filter(f => f.id !== file.id))}
                className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default FileUpload
