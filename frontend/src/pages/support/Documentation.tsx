import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { documentationAPI } from '@/lib/api'
import { Plus, Search, Download, FileText, Upload, Trash, Eye } from 'lucide-react'
import toast from 'react-hot-toast'

interface Document {
  id: number
  title: string
  description: string
  category: string
  file_url: string
  file_size: number
  file_type: string
  views: number
  created_at: string
  updated_at: string
}

const categories = ['User Guides', 'API Docs', 'Admin Guides', 'Videos', 'Policies']

export default function Documentation() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    file: null as File | null,
  })

  // Fetch documents
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['documents', categoryFilter],
    queryFn: () =>
      documentationAPI.getAll({
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
      }),
  })

  // Create document mutation
  const createMutation = useMutation({
    mutationFn: documentationAPI.create,
    onSuccess: () => {
      toast.success('Document uploaded successfully')
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setShowCreateModal(false)
      resetForm()
    },
    onError: () => {
      toast.error('Failed to upload document')
    },
  })

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: documentationAPI.delete,
    onSuccess: () => {
      toast.success('Document deleted successfully')
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
    onError: () => {
      toast.error('Failed to delete document')
    },
  })

  // Track view mutation
  const trackViewMutation = useMutation({
    mutationFn: documentationAPI.trackView,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: '',
      file: null,
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title || !formData.category || !formData.file) {
      toast.error('Please fill all required fields')
      return
    }

    const formDataToSend = new FormData()
    formDataToSend.append('title', formData.title)
    formDataToSend.append('description', formData.description)
    formDataToSend.append('category', formData.category)
    formDataToSend.append('file', formData.file)

    createMutation.mutate(formDataToSend as any)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file size (max 50MB)
      if (file.size > 50 * 1024 * 1024) {
        toast.error('File size must be less than 50MB')
        return
      }
      setFormData({ ...formData, file })
    }
  }

  const handleDownload = (doc: Document) => {
    trackViewMutation.mutate(doc.id)
    window.open(doc.file_url, '_blank')
  }

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getFileIcon = (_fileType: string) => {
    return <FileText className="w-8 h-8 text-blue-500" />
  }

  // Filter documents based on search query
  const filteredDocuments = documents?.filter((doc: Document) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  }) || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center text-red-600">
        Error loading documents: {(error as Error).message}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Documentation</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Search</label>
              <Input
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={<Search className="w-4 h-4" />}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Category</label>
              <Select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Categories' },
                  ...categories.map(cat => ({ value: cat, label: cat })),
                ]}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Document Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDocuments.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="pt-6 text-center py-12">
              <p className="text-gray-500">No documents found</p>
              <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                Upload your first document
              </Button>
            </CardContent>
          </Card>
        ) : (
          filteredDocuments.map((doc: Document) => (
            <Card key={doc.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    {getFileIcon(doc.file_type)}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <Trash className="w-4 h-4" />
                    </Button>
                  </div>

                  <div>
                    <h3 className="font-semibold text-lg mb-2">{doc.title}</h3>
                    <p className="text-sm text-gray-600 line-clamp-2">{doc.description}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant="default">{doc.category}</Badge>
                    <span className="text-xs text-gray-500">{formatFileSize(doc.file_size)}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      <span>{doc.views} views</span>
                    </div>
                    <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                  </div>

                  <Button
                    className="w-full"
                    onClick={() => handleDownload(doc)}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Upload Document Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          resetForm()
        }}
        title="Upload Document"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Document title"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Description
            </label>
            <textarea
              className="w-full border rounded-md p-2 min-h-[100px]"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the document"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <Select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              options={[
                { value: '', label: 'Select Category' },
                ...categories.map(cat => ({ value: cat, label: cat })),
              ]}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              File <span className="text-red-500">*</span>
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-md p-6 text-center">
              <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm text-gray-600 mb-2">
                {formData.file ? formData.file.name : 'Click to upload or drag and drop'}
              </p>
              <p className="text-xs text-gray-500">PDF, DOCX, MP4 (max 50MB)</p>
              <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.doc,.docx,.mp4,.mov"
                className="hidden"
                id="file-upload"
                required
              />
              <Button
                type="button"
                variant="outline"
                className="mt-2"
                onClick={() => document.getElementById('file-upload')?.click()}
              >
                Select File
              </Button>
            </div>
          </div>

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowCreateModal(false)
                resetForm()
              }}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Uploading...' : 'Upload Document'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
