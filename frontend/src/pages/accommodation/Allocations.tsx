import { useState } from 'react'
import { Plus, Search, Trash2, ArrowRight, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { AllocationForm } from '@/components/forms/AllocationForm'

const allocationsAPI = {
  getAll: async (_skip = 0, _limit = 100) => [],
  create: async (data: any) => ({ id: Date.now(), ...data }),
  update: async (_id: number, data: any) => ({ id: Date.now(), ...data }),
  delete: async (_id: number) => {},
}

export default function Allocations() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false)
  const [selectedAllocation, setSelectedAllocation] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [editingAllocation, _setEditingAllocation] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: allocations,
    filteredData,
  } = useDataTable({
    queryKey: 'allocations',
    queryFn: allocationsAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleCreate, handleUpdate } = useCRUD({
    queryKey: 'allocations',
    entityName: 'Allocation',
    create: allocationsAPI.create,
    update: allocationsAPI.update,
    delete: allocationsAPI.delete,
  })

  const handleTransfer = async (newBedId: string) => {
    if (!selectedAllocation) return

    await handleUpdate(selectedAllocation.id, { end_date: new Date().toISOString(), status: 'ended' })
    await handleCreate({
      courier_id: selectedAllocation.courier_id,
      bed_id: newBedId,
      start_date: new Date().toISOString(),
      status: 'active'
    })

    setIsTransferModalOpen(false)
    setSelectedAllocation(null)
  }

  const handleEndAllocation = async (id: number) => {
    await handleUpdate(id, { end_date: new Date().toISOString(), status: 'ended' })
  }

  const columns = [
    {
      key: 'courier_name',
      header: 'Courier Name',
      sortable: true,
    },
    {
      key: 'building',
      header: 'Building',
      render: (row: any) => row.building_name || 'N/A',
    },
    {
      key: 'room',
      header: 'Room',
      render: (row: any) => row.room_number || 'N/A',
    },
    {
      key: 'bed',
      header: 'Bed',
      render: (row: any) => row.bed_number || 'N/A',
    },
    {
      key: 'start_date',
      header: 'Start Date',
      render: (row: any) => row.start_date ? new Date(row.start_date).toLocaleDateString() : 'N/A',
    },
    {
      key: 'end_date',
      header: 'End Date',
      render: (row: any) => row.end_date ? new Date(row.end_date).toLocaleDateString() : '-',
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={row.status === 'active' ? 'success' : row.status === 'pending' ? 'warning' : 'default'}>
          {row.status}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          {row.status === 'active' && (
            <>
              <Button size="sm" variant="ghost" onClick={() => { setSelectedAllocation(row); setIsTransferModalOpen(true); }} title="Transfer">
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="ghost" onClick={() => handleEndAllocation(row.id)} title="End Allocation">
                <X className="h-4 w-4 text-red-600" />
              </Button>
            </>
          )}
          <Button size="sm" variant="ghost" onClick={() => handleDelete(row.id)}>
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
      ),
    },
  ]

  if (isLoading) return <div className="flex items-center justify-center h-64"><Spinner /></div>
  if (error) return <div className="p-4 bg-red-50 border border-red-200 rounded-lg"><p className="text-red-800">Error: {error.message}</p></div>

  const activeAllocations = filteredData.filter((a: any) => a.status === 'active').length
  const pendingAllocations = filteredData.filter((a: any) => a.status === 'pending').length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Allocations</h1>
        <Button onClick={() => setIsModalOpen(true)}><Plus className="h-4 w-4 mr-2" />New Allocation</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-green-600">{activeAllocations}</p><p className="text-sm text-gray-600">Active Allocations</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-yellow-600">{pendingAllocations}</p><p className="text-sm text-gray-600">Pending Transfers</p></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Allocations</CardTitle></CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <Input placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} leftIcon={<Search className="h-4 w-4 text-gray-400" />} className="flex-1" />
            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} options={[{value: 'all', label: 'All Status'}, {value: 'active', label: 'Active'}, {value: 'ended', label: 'Ended'}, {value: 'pending', label: 'Pending'}]} className="w-48" />
          </div>
          <Table data={allocations} columns={columns} />
          <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} totalItems={filteredData.length} pageSize={pageSize} />
        </CardContent>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="New Allocation" size="lg">
        <AllocationForm initialData={editingAllocation} onSubmit={async (data) => { await handleCreate(data); setIsModalOpen(false); }} onCancel={() => setIsModalOpen(false)} />
      </Modal>

      <Modal isOpen={isTransferModalOpen} onClose={() => setIsTransferModalOpen(false)} title="Transfer Allocation" size="md">
        <div className="space-y-4">
          <p>Transfer {selectedAllocation?.courier_name} to a new bed</p>
          <Button onClick={() => handleTransfer('new-bed-id')}>Confirm Transfer</Button>
        </div>
      </Modal>
    </div>
  )
}
