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
import { bonusesAPI, couriersAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { BonusForm } from '@/components/forms'

export default function Bonuses() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedBonus, setSelectedBonus] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: bonuses,
    filteredData,
  } = useDataTable({
    queryKey: 'bonuses',
    queryFn: bonusesAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'bonuses',
    entityName: 'Bonus',
    create: bonusesAPI.create,
    update: bonusesAPI.update,
    delete: bonusesAPI.delete,
  })

  const { data: couriers = [] } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  const handleEdit = (bonus: any) => {
    setSelectedBonus(bonus)
    setIsModalOpen(true)
  }

  const handleApprove = async (id: number) => {
    await handleUpdate(id, { status: 'approved' })
  }

  const handleReject = async (id: number) => {
    await handleUpdate(id, { status: 'rejected' })
  }

  const onSubmit = async (data: any) => {
    if (selectedBonus) {
      await handleUpdate(selectedBonus.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedBonus(null)
  }

  const columns = [
    {
      key: 'courier_id',
      header: 'Courier ID',
      sortable: true,
    },
    {
      key: 'bonus_type',
      header: 'Type',
      render: (row: any) => row.bonus_type || 'N/A',
    },
    {
      key: 'bonus_date',
      header: 'Date',
      render: (row: any) => row.bonus_date ? new Date(row.bonus_date).toLocaleDateString() : 'N/A',
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (row: any) => row.amount ? `SAR ${Number(row.amount).toFixed(2)}` : 'N/A',
    },
    {
      key: 'description',
      header: 'Description',
      render: (row: any) => row.description || 'N/A',
    },
    {
      key: 'payment_status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.payment_status === 'approved' || row.payment_status === 'paid'
              ? 'success'
              : row.payment_status === 'pending'
              ? 'warning'
              : 'default'
          }
        >
          {row.payment_status || 'pending'}
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
          Error loading bonuses: {error.message}
        </p>
      </div>
    )
  }

  const pendingCount = bonuses.filter((b: any) => b.payment_status === 'pending').length
  const approvedCount = bonuses.filter((b: any) => b.payment_status === 'approved' || b.payment_status === 'paid').length
  const totalAmount = bonuses.reduce((sum: number, b: any) => sum + (b.amount || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Bonus Management</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => { setSelectedBonus(null); setIsModalOpen(true) }}>
            <Plus className="h-4 w-4 mr-2" />
            New Bonus
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {bonuses.length}
              </p>
              <p className="text-sm text-gray-600">Total Bonuses</p>
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
              <p className="text-2xl font-bold text-blue-600">
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
              placeholder="Search bonuses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={bonuses} columns={columns} />
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
        title={selectedBonus ? 'Edit Bonus' : 'New Bonus'}
        size="lg"
      >
        <BonusForm
          initialData={selectedBonus}
          onSubmit={onSubmit}
          onCancel={() => {
            setIsModalOpen(false)
            setSelectedBonus(null)
          }}
          isLoading={isLoading}
          couriers={couriers}
        />
      </Modal>
    </div>
  )
}
