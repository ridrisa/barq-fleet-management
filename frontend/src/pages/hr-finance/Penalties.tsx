import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Download, CheckCircle, XCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { penaltiesAPI, couriersAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { PenaltyForm } from '@/components/forms'

export default function Penalties() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedPenalty, setSelectedPenalty] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: penalties,
    filteredData,
  } = useDataTable({
    queryKey: 'penalties',
    queryFn: penaltiesAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'penalties',
    entityName: 'Penalty',
    create: penaltiesAPI.create,
    update: penaltiesAPI.update,
    delete: penaltiesAPI.delete,
  })

  const { data: couriers = [] } = useQuery({
    queryKey: ['couriers'],
    queryFn: couriersAPI.getAll,
  })

  const handleEdit = (penalty: any) => {
    setSelectedPenalty(penalty)
    setIsModalOpen(true)
  }

  const handleApprove = async (id: number) => {
    await handleUpdate(id, { status: 'approved' })
  }

  const handleReject = async (id: number) => {
    await handleUpdate(id, { status: 'rejected' })
  }

  const onSubmit = async (data: any) => {
    if (selectedPenalty) {
      await handleUpdate(selectedPenalty.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedPenalty(null)
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
      key: 'penalty_type',
      header: 'Type',
      render: (row: any) => row.penalty_type || 'N/A',
    },
    {
      key: 'reason',
      header: 'Reason',
      render: (row: any) => row.reason || 'N/A',
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (row: any) => row.amount ? `SAR ${Number(row.amount).toFixed(2)}` : 'N/A',
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
          Error loading penalties: {error.message}
        </p>
      </div>
    )
  }

  const pendingCount = penalties.filter((p: any) => p.status === 'pending').length
  const approvedCount = penalties.filter((p: any) => p.status === 'approved').length
  const totalAmount = penalties.reduce((sum: number, p: any) => sum + (p.amount || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Penalties</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => { setSelectedPenalty(null); setIsModalOpen(true) }}>
            <Plus className="h-4 w-4 mr-2" />
            New Penalty
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {penalties.length}
              </p>
              <p className="text-sm text-gray-600">Total Penalties</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {pendingCount}
              </p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {approvedCount}
              </p>
              <p className="text-sm text-gray-600">Approved</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                ${totalAmount.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600">Total Amount</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4">
            <Input
              placeholder="Search penalties..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={penalties} columns={columns} />
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
        title={selectedPenalty ? 'Edit Penalty' : 'New Penalty'}
        size="lg"
      >
        <PenaltyForm
          initialData={selectedPenalty}
          onSubmit={onSubmit}
          onCancel={() => {
            setIsModalOpen(false)
            setSelectedPenalty(null)
          }}
          isLoading={isLoading}
          couriers={couriers}
        />
      </Modal>
    </div>
  )
}
