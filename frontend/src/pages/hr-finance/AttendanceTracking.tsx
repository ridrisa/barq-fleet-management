import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Download } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { attendanceAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { AttendanceForm, AttendanceFormData } from '@/components/forms/AttendanceForm'

export default function AttendanceTracking() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<any>(null)
  const [filterDate, setFilterDate] = useState('')

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: attendance,
    filteredData,
  } = useDataTable({
    queryKey: 'attendance',
    queryFn: attendanceAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'attendance',
    entityName: 'Attendance',
    create: attendanceAPI.create,
    update: attendanceAPI.update,
    delete: attendanceAPI.delete,
  })

  const handleEdit = (record: any) => {
    setSelectedRecord(record)
    setIsModalOpen(true)
  }

  const handleNewRecord = () => {
    setSelectedRecord(null)
    setIsModalOpen(true)
  }

  const handleFormSubmit = async (data: AttendanceFormData) => {
    if (selectedRecord) {
      await handleUpdate(selectedRecord.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedRecord(null)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedRecord(null)
  }

  const columns = [
    {
      key: 'date',
      header: 'Date',
      sortable: true,
      render: (row: any) => {
        if (!row.date) return 'N/A'
        return new Date(row.date).toLocaleDateString()
      },
    },
    {
      key: 'courier_id',
      header: 'Courier ID',
      sortable: true,
    },
    {
      key: 'courier_name',
      header: 'Courier Name',
      render: (row: any) => row.courier_name || 'N/A',
    },
    {
      key: 'check_in',
      header: 'Check In',
      render: (row: any) => {
        if (!row.check_in) return 'N/A'
        return new Date(row.check_in).toLocaleTimeString()
      },
    },
    {
      key: 'check_out',
      header: 'Check Out',
      render: (row: any) => {
        if (!row.check_out) return 'Pending'
        return new Date(row.check_out).toLocaleTimeString()
      },
    },
    {
      key: 'hours_worked',
      header: 'Hours',
      render: (row: any) => {
        if (!row.check_in || !row.check_out) return 'N/A'
        const hours = (new Date(row.check_out).getTime() - new Date(row.check_in).getTime()) / (1000 * 60 * 60)
        return hours.toFixed(2)
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const status = row.status || 'present'
        let variant: 'success' | 'warning' | 'danger' | 'default' = 'default'

        if (status === 'present') variant = 'success'
        else if (status === 'late') variant = 'warning'
        else if (status === 'absent') variant = 'danger'

        return (
          <Badge variant={variant}>
            {status}
          </Badge>
        )
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleEdit(row)}
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
        <p className="text-red-800">
          Error loading attendance records: {error.message}
        </p>
      </div>
    )
  }

  const presentCount = attendance.filter((a: any) => a.status === 'present').length
  const lateCount = attendance.filter((a: any) => a.status === 'late').length
  const absentCount = attendance.filter((a: any) => a.status === 'absent').length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Attendance Tracking</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleNewRecord}>
            <Plus className="h-4 w-4 mr-2" />
            New Record
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {attendance.length}
              </p>
              <p className="text-sm text-gray-600">Total Records</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {presentCount}
              </p>
              <p className="text-sm text-gray-600">Present</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {lateCount}
              </p>
              <p className="text-sm text-gray-600">Late</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {absentCount}
              </p>
              <p className="text-sm text-gray-600">Absent</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search attendance..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <Input
              type="date"
              value={filterDate}
              onChange={(e) => setFilterDate(e.target.value)}
              className="w-48"
            />
          </div>
          <Table data={attendance} columns={columns} />
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
        onClose={handleModalClose}
        title={selectedRecord ? 'Edit Attendance' : 'New Attendance Record'}
        size="lg"
      >
        <AttendanceForm
          initialData={selectedRecord}
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          mode={selectedRecord ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  )
}
