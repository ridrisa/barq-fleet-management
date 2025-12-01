import { useState } from 'react'
import { Plus, Search, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { FileUpload } from '@/components/ui/FileUpload'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { maintenanceAPI } from '@/lib/api'

export default function Maintenance() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')

  const { isLoading, error, currentPage, pageSize, totalPages, searchTerm, setSearchTerm, setCurrentPage, paginatedData: maintenance, filteredData } = useDataTable({
    queryKey: 'maintenance',
    queryFn: maintenanceAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate: _handleCreate } = useCRUD({
    queryKey: 'maintenance',
    entityName: 'Maintenance Request',
    create: maintenanceAPI.create,
    update: maintenanceAPI.update,
    delete: maintenanceAPI.delete,
  })

  const getPriorityBadgeVariant = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'danger'
      case 'high': return 'warning'
      case 'medium': return 'info'
      case 'low': return 'default'
      default: return 'default'
    }
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'pending': return 'warning'
      case 'in-progress': return 'info'
      case 'completed': return 'success'
      default: return 'default'
    }
  }

  const columns = [
    { key: 'building', header: 'Building', render: (row: any) => row.building_name || 'N/A' },
    { key: 'location', header: 'Room/Bed', render: (row: any) => `Room ${row.room_number}` + (row.bed_number ? ` / Bed ${row.bed_number}` : '') },
    { key: 'issue', header: 'Issue', sortable: true },
    { key: 'reported_date', header: 'Reported Date', render: (row: any) => row.reported_date ? new Date(row.reported_date).toLocaleDateString() : 'N/A' },
    { key: 'status', header: 'Status', render: (row: any) => <Badge variant={getStatusBadgeVariant(row.status)}>{row.status}</Badge> },
    { key: 'assigned_to', header: 'Assigned To', render: (row: any) => row.assigned_to || '-' },
    { key: 'priority', header: 'Priority', render: (row: any) => <Badge variant={getPriorityBadgeVariant(row.priority)}><AlertCircle className="h-3 w-3 mr-1 inline" />{row.priority}</Badge> },
  ]

  if (isLoading) return <div className="flex items-center justify-center h-64"><Spinner /></div>
  if (error) return <div className="p-4 bg-red-50 border border-red-200 rounded-lg"><p className="text-red-800">Error: {error.message}</p></div>

  const openIssues = filteredData.filter((m: any) => m.status !== 'completed').length
  const avgResolutionTime = 3.5

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Maintenance</h1>
        <Button onClick={() => setIsModalOpen(true)}><Plus className="h-4 w-4 mr-2" />New Request</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-red-600">{openIssues}</p><p className="text-sm text-gray-600">Open Issues</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-blue-600">{avgResolutionTime} days</p><p className="text-sm text-gray-600">Avg Resolution Time</p></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Maintenance Requests</CardTitle></CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <Input placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} leftIcon={<Search className="h-4 w-4 text-gray-400" />} className="flex-1" />
            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} options={[{value: 'all', label: 'All Status'}, {value: 'pending', label: 'Pending'}, {value: 'in-progress', label: 'In Progress'}, {value: 'completed', label: 'Completed'}]} className="w-48" />
            <Select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)} options={[{value: 'all', label: 'All Priority'}, {value: 'urgent', label: 'Urgent'}, {value: 'high', label: 'High'}, {value: 'medium', label: 'Medium'}, {value: 'low', label: 'Low'}]} className="w-48" />
          </div>
          <Table data={maintenance} columns={columns} />
          <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} totalItems={filteredData.length} pageSize={pageSize} />
        </CardContent>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="New Maintenance Request" size="md">
        <div className="space-y-4">
          <Input placeholder="Issue description" />
          <Select options={[{value: 'urgent', label: 'Urgent'}, {value: 'high', label: 'High'}, {value: 'medium', label: 'Medium'}, {value: 'low', label: 'Low'}]} />
          <FileUpload onFilesSelected={(files) => console.log(files)} accept={{ 'image/*': ['.png', '.jpg'] }} maxFiles={5} />
          <Button onClick={() => setIsModalOpen(false)}>Submit Request</Button>
        </div>
      </Modal>
    </div>
  )
}
