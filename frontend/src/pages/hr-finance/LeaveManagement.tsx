import { useState } from 'react'
import { Plus, Search, Edit, Trash2, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { leavesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

export default function LeaveManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Use the reusable data table hook
  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: leaves,
    filteredData,
  } = useDataTable({
    queryKey: 'leaves',
    queryFn: leavesAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleDelete, handleUpdate } = useCRUD({
    queryKey: 'leaves',
    entityName: 'Leave Request',
    create: leavesAPI.create,
    update: leavesAPI.update,
    delete: leavesAPI.delete,
  })

  // Handle approve/reject actions
  const handleApprove = async (id: number) => {
    await handleUpdate(id, { status: 'approved' })
  }

  const handleReject = async (id: number) => {
    await handleUpdate(id, { status: 'rejected' })
  }

  const columns = [
    {
      key: 'employee_id',
      header: 'Employee ID',
      sortable: true,
    },
    {
      key: 'employee_name',
      header: 'Employee Name',
      render: (row: any) => row.employee_name || 'N/A',
    },
    {
      key: 'leave_type',
      header: 'Leave Type',
      render: (row: any) => (
        <Badge variant="default">
          {row.leave_type || 'general'}
        </Badge>
      ),
    },
    {
      key: 'start_date',
      header: 'Start Date',
      render: (row: any) => {
        if (!row.start_date) return 'N/A'
        return new Date(row.start_date).toLocaleDateString()
      },
    },
    {
      key: 'end_date',
      header: 'End Date',
      render: (row: any) => {
        if (!row.end_date) return 'N/A'
        return new Date(row.end_date).toLocaleDateString()
      },
    },
    {
      key: 'days',
      header: 'Days',
      render: (row: any) => {
        if (!row.start_date || !row.end_date) return 'N/A'
        const start = new Date(row.start_date)
        const end = new Date(row.end_date)
        const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1
        return days
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'approved'
              ? 'success'
              : row.status === 'rejected'
              ? 'danger'
              : row.status === 'pending'
              ? 'warning'
              : 'default'
          }
        >
          {row.status || 'pending'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          {row.status === 'pending' && (
            <>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleApprove(row.id)}
                title="Approve"
              >
                <CheckCircle className="h-4 w-4 text-green-600" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => handleReject(row.id)}
                title="Reject"
              >
                <XCircle className="h-4 w-4 text-red-600" />
              </Button>
            </>
          )}
          <Button size="sm" variant="ghost">
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
        <p className="text-red-800">
          Error loading leave requests: {error.message}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Leave Management</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Leave Request
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {leaves.length}
              </p>
              <p className="text-sm text-gray-600">Total Requests</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {leaves.filter((l: any) => l.status === 'pending').length}
              </p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {leaves.filter((l: any) => l.status === 'approved').length}
              </p>
              <p className="text-sm text-gray-600">Approved</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {leaves.filter((l: any) => l.status === 'rejected').length}
              </p>
              <p className="text-sm text-gray-600">Rejected</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Leave Requests</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search leave requests..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={leaves} columns={columns} />
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
        onClose={() => setIsModalOpen(false)}
        title="New Leave Request"
        size="lg"
      >
        <p>Leave request form will be here</p>
      </Modal>
    </div>
  )
}
