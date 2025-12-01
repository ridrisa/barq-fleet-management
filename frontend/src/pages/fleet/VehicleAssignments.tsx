import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { assignmentsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { AssignmentForm, AssignmentFormData } from '@/components/forms/AssignmentForm'

export default function VehicleAssignments() {
  const { t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingAssignment, setEditingAssignment] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: assignments,
    filteredData,
  } = useDataTable({
    queryKey: 'assignments',
    queryFn: assignmentsAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'assignments',
    entityName: 'Assignment',
    create: assignmentsAPI.create,
    update: assignmentsAPI.update,
    delete: assignmentsAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingAssignment(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (assignment: any) => {
    setEditingAssignment(assignment)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingAssignment(null)
  }

  const handleFormSubmit = async (data: AssignmentFormData) => {
    if (editingAssignment) {
      const result = await handleUpdate(editingAssignment.id, data)
      if (result) {
        handleCloseModal()
      }
    } else {
      const result = await handleCreate(data)
      if (result) {
        handleCloseModal()
      }
    }
  }

  const columns = [
    { key: 'courier_id', header: 'Courier ID', sortable: true },
    { key: 'vehicle_id', header: 'Vehicle ID', sortable: true },
    { key: 'start_date', header: 'Start Date' },
    { key: 'end_date', header: 'End Date' },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'active'
              ? 'success'
              : 'default'
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
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
          >
            <Edit className="h-4 w-4" />
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
        <p className="text-red-800">Error loading assignments: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('nav.assignments')}</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          New Assignment
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Assignments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search assignments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={assignments} columns={columns} />
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
        title={editingAssignment ? 'Edit Assignment' : 'Add New Assignment'}
        size="lg"
      >
        <AssignmentForm
          initialData={editingAssignment}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingAssignment ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  )
}