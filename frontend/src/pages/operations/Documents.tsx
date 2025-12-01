import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, Edit, Trash2, Download, Upload, FileText, Filter, FolderOpen } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { documentationAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { DocumentUploadForm } from '@/components/forms/DocumentUploadForm'

export default function Documents() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDocument, setEditingDocument] = useState<any>(null)
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('all')

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
  } = useDataTable({
    queryKey: 'operations-documents',
    queryFn: () => documentationAPI.getAll(),
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'operations-documents',
    entityName: 'Document',
    create: documentationAPI.create,
    update: documentationAPI.update,
    delete: documentationAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingDocument(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (document: any) => {
    setEditingDocument(document)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingDocument(null)
  }

  const handleSubmit = async (data: any) => {
    if (editingDocument) {
      await handleUpdate(editingDocument.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  const handleDownload = (document: any) => {
    console.log('Downloading document:', document)
    // Download functionality will be implemented with actual file handling
  }

  // Apply filters
  let displayData = filteredData
  if (categoryFilter !== 'all') {
    displayData = displayData.filter((d: any) => d.category === categoryFilter)
  }
  if (fileTypeFilter !== 'all') {
    displayData = displayData.filter((d: any) => {
      const extension = d.file_name?.split('.').pop()?.toLowerCase()
      return extension === fileTypeFilter
    })
  }

  // Summary stats
  const stats = {
    total: filteredData.length,
    procedures: filteredData.filter((d: any) => d.category === 'Procedures').length,
    policies: filteredData.filter((d: any) => d.category === 'Policies').length,
    training: filteredData.filter((d: any) => d.category === 'Training').length,
    reports: filteredData.filter((d: any) => d.category === 'Reports').length,
  }

  const getCategoryVariant = (category: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      Procedures: 'default',
      Policies: 'warning',
      Training: 'success',
      Reports: 'danger',
    }
    return variants[category] || 'default'
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const getFileIcon = (_fileName: string) => {
    return <FileText className="h-5 w-5 text-blue-600" />
  }

  const columns = [
    {
      key: 'doc_id',
      header: 'Document ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.doc_number || `DOC-${row.id?.toString().padStart(5, '0')}`}
        </div>
      ),
    },
    {
      key: 'doc_name',
      header: 'Document Name',
      render: (row: any) => (
        <div className="flex items-center gap-2">
          {getFileIcon(row.file_name || '')}
          <div>
            <div className="font-medium text-gray-900">{row.doc_name || 'Untitled'}</div>
            <div className="text-xs text-gray-500">{row.file_name || ''}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      render: (row: any) => (
        <Badge variant={getCategoryVariant(row.category)}>
          {row.category || 'Uncategorized'}
        </Badge>
      ),
    },
    {
      key: 'uploaded_by',
      header: 'Uploaded By',
      render: (row: any) => (
        <div>
          <div className="font-medium text-gray-900">{row.uploaded_by || 'N/A'}</div>
          <div className="text-xs text-gray-500">{row.uploader_email || ''}</div>
        </div>
      ),
    },
    {
      key: 'upload_date',
      header: 'Upload Date',
      sortable: true,
      render: (row: any) => {
        const date = row.upload_date || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'file_size',
      header: 'File Size',
      render: (row: any) => {
        const size = row.file_size || 0
        return <span className="text-gray-700">{formatFileSize(size)}</span>
      },
    },
    {
      key: 'version',
      header: 'Version',
      render: (row: any) => (
        <div className="text-center">
          <Badge variant="default">v{row.version || '1.0'}</Badge>
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDownload(row)}
            title="Download"
          >
            <Download className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
            title="Edit"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete"
          >
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading documents: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Operations Documents</h1>
        <Button onClick={handleOpenCreateModal}>
          <Upload className="h-4 w-4 mr-2" />
          Upload Document
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <FolderOpen className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Procedures</p>
                <p className="text-2xl font-bold text-blue-600">{stats.procedures}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Policies</p>
                <p className="text-2xl font-bold text-orange-600">{stats.policies}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Training</p>
                <p className="text-2xl font-bold text-green-600">{stats.training}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Document Library */}
      <Card>
        <CardHeader>
          <CardTitle>Document Library</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Categories' },
                    { value: 'Procedures', label: 'Procedures' },
                    { value: 'Policies', label: 'Policies' },
                    { value: 'Training', label: 'Training' },
                    { value: 'Reports', label: 'Reports' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={fileTypeFilter}
                  onChange={(e) => setFileTypeFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All File Types' },
                    { value: 'pdf', label: 'PDF' },
                    { value: 'doc', label: 'Word' },
                    { value: 'docx', label: 'Word (DOCX)' },
                    { value: 'xls', label: 'Excel' },
                    { value: 'xlsx', label: 'Excel (XLSX)' },
                    { value: 'ppt', label: 'PowerPoint' },
                    { value: 'txt', label: 'Text' },
                  ]}
                />
              </div>
            </div>

            <Table
              data={displayData.slice((currentPage - 1) * pageSize, currentPage * pageSize)}
              columns={columns}
            />

            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(displayData.length / pageSize)}
              onPageChange={setCurrentPage}
              totalItems={displayData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>

      {/* Upload/Edit Document Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingDocument ? 'Edit Document' : 'Upload New Document'}
        size="lg"
      >
        <DocumentUploadForm
          initialData={editingDocument}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
        />
      </Modal>
    </div>
  )
}
