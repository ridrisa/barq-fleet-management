import { forwardRef, useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/cn'

export interface FileUploadProps {
  onFilesSelected: (files: File[]) => void
  accept?: Record<string, string[]>
  maxFiles?: number
  maxSize?: number
  multiple?: boolean
  className?: string
  disabled?: boolean
  showPreview?: boolean
}

interface FileWithPreview extends File {
  preview?: string
}

export const FileUpload = forwardRef<HTMLDivElement, FileUploadProps>(
  (
    {
      onFilesSelected,
      accept,
      maxFiles = 10,
      maxSize = 5242880, // 5MB default
      multiple = true,
      className,
      disabled = false,
      showPreview = true,
    },
    ref
  ) => {
    const [files, setFiles] = useState<FileWithPreview[]>([])
    const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

    const onDrop = useCallback(
      (acceptedFiles: File[]) => {
        const filesWithPreview = acceptedFiles.map((file) => {
          const fileWithPreview = file as FileWithPreview

          // Create preview for images
          if (file.type.startsWith('image/')) {
            fileWithPreview.preview = URL.createObjectURL(file)
          }

          return fileWithPreview
        })

        setFiles((prev) => [...prev, ...filesWithPreview])
        onFilesSelected(acceptedFiles)

        // Simulate upload progress
        acceptedFiles.forEach((file) => {
          let progress = 0
          const interval = setInterval(() => {
            progress += 10
            setUploadProgress((prev) => ({ ...prev, [file.name]: progress }))
            if (progress >= 100) {
              clearInterval(interval)
            }
          }, 100)
        })
      },
      [onFilesSelected]
    )

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
      onDrop,
      accept,
      maxFiles,
      maxSize,
      multiple,
      disabled,
    })

    const removeFile = (fileName: string) => {
      setFiles((prev) => {
        const updated = prev.filter((file) => file.name !== fileName)
        // Revoke preview URL to avoid memory leaks
        const removed = prev.find((file) => file.name === fileName)
        if (removed?.preview) {
          URL.revokeObjectURL(removed.preview)
        }
        return updated
      })
      setUploadProgress((prev) => {
        const { [fileName]: _, ...rest } = prev
        return rest
      })
    }

    const formatFileSize = (bytes: number): string => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    }

    return (
      <div ref={ref} className={cn('w-full', className)}>
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive && !isDragReject && 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
            isDragReject && 'border-red-500 bg-red-50 dark:bg-red-900/20',
            !isDragActive && 'border-gray-300 hover:border-gray-400 dark:border-gray-600',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
          role="button"
          aria-label="File upload area"
          tabIndex={0}
        >
          <input {...getInputProps()} aria-label="File input" />

          <div className="space-y-2">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            {isDragActive ? (
              <p className="text-blue-600 dark:text-blue-400 font-medium">
                Drop files here...
              </p>
            ) : (
              <>
                <p className="text-gray-700 dark:text-gray-300">
                  <span className="font-medium text-blue-600 dark:text-blue-400">
                    Click to upload
                  </span>{' '}
                  or drag and drop
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {multiple ? `Up to ${maxFiles} files` : 'Single file'} (max {formatFileSize(maxSize)} each)
                </p>
              </>
            )}
          </div>
        </div>

        {showPreview && files.length > 0 && (
          <div className="mt-4 space-y-2" role="list" aria-label="Uploaded files">
            {files.map((file) => (
              <div
                key={file.name}
                className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                role="listitem"
              >
                {file.preview ? (
                  <img
                    src={file.preview}
                    alt={file.name}
                    className="w-12 h-12 object-cover rounded"
                  />
                ) : (
                  <div className="w-12 h-12 flex items-center justify-center bg-gray-200 dark:bg-gray-700 rounded">
                    <svg
                      className="w-6 h-6 text-gray-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatFileSize(file.size)}
                  </p>

                  {uploadProgress[file.name] !== undefined && uploadProgress[file.name] < 100 && (
                    <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full transition-all"
                        style={{ width: `${uploadProgress[file.name]}%` }}
                        role="progressbar"
                        aria-valuenow={uploadProgress[file.name]}
                        aria-valuemin={0}
                        aria-valuemax={100}
                      />
                    </div>
                  )}
                </div>

                <button
                  onClick={() => removeFile(file.name)}
                  className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  aria-label={`Remove ${file.name}`}
                  type="button"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }
)

FileUpload.displayName = 'FileUpload'
