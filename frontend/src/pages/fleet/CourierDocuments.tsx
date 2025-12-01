import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Search, Trash2, Download, Upload } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { documentsAPI, couriersAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { CourierDocumentForm } from '@/components/forms'

export default function CourierDocuments() {
  const { t: _t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDocument, setEditingDocument] = useState<any>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Fetch couriers for the form dropdown
  const { data: couriersData } = useQuery({
    queryKey: ['couriers'],
    queryFn: couriersAPI.getAll,
  })

  const couriers = couriersData?.map((courier: any) => ({
    id: courier.id.toString(),
    name: courier.name,
  })) || []

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: documents,
    filteredData,
  } = useDataTable({
    queryKey: 'documents',
    queryFn: documentsAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete } = useCRUD({
    queryKey: 'documents',
    entityName: 'Document',
    create: documentsAPI.create,
    update: documentsAPI.update,
    delete: documentsAPI.delete,
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

  const handleFormSubmit = async (data: any) => {
    setIsSubmitting(true)
    try {
      if (editingDocument?.id) {
        await handleUpdate(editingDocument.id, data)
      } else {
        await handleCreate(data)
      }
      handleCloseModal()
    } finally {
      setIsSubmitting(false)
    }
  }

  const columns = [
    { key: 'courier_id', header: 'Courier ID', sortable: true },
    { key: 'document_type', header: 'Document Type' },
    { key: 'expiry_date', header: 'Expiry Date' },
    { key: 'upload_date', header: 'Upload Date' },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'valid'
              ? 'success'
              : row.status === 'expiring_soon'
              ? 'warning'
              : 'danger'
          }
        >
          {row.status}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button size="sm" variant="ghost">
            <Download className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
          >
            <Upload className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
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
        <h1 className="text-2xl font-bold">Courier Documents</h1>
        <Button onClick={handleOpenCreateModal}>
          <Upload className="h-4 w-4 mr-2" />
          Upload Document
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {documents.filter((d: any) => d.status === 'valid').length}
            </div>
            <p className="text-sm text-gray-600">Valid Documents</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-yellow-600">
              {documents.filter((d: any) => d.status === 'expiring_soon').length}
            </div>
            <p className="text-sm text-gray-600">Expiring Soon</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">
              {documents.filter((d: any) => d.status === 'expired').length}
            </div>
            <p className="text-sm text-gray-600">Expired</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={documents} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingDocument ? 'Edit Document' : 'Upload Document'}
        size="lg"
      >
        <CourierDocumentForm
          initialData={editingDocument}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isSubmitting}
          couriers={couriers}
        />
      </Modal>
    </div>
  )
}