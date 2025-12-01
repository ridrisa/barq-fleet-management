import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Download, Upload, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { expensesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { ExpenseForm } from '@/components/forms'

export default function ExpenseTracking() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedExpense, setSelectedExpense] = useState<any>(null)
  const [categoryFilter, setCategoryFilter] = useState('')

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: expenses,
    filteredData,
  } = useDataTable({
    queryKey: 'expenses',
    queryFn: expensesAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'expenses',
    entityName: 'Expense',
    create: expensesAPI.create,
    update: expensesAPI.update,
    delete: expensesAPI.delete,
  })

  const handleEdit = (expense: any) => {
    setSelectedExpense(expense)
    setIsModalOpen(true)
  }

  const handleApprove = async (id: number) => {
    await handleUpdate(id, { status: 'approved' })
  }

  const handleReject = async (id: number) => {
    await handleUpdate(id, { status: 'rejected' })
  }

  const onSubmit = async (data: any) => {
    if (selectedExpense) {
      await handleUpdate(selectedExpense.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedExpense(null)
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
      key: 'category',
      header: 'Category',
      render: (row: any) => (
        <Badge variant="default">{row.category || 'general'}</Badge>
      ),
    },
    {
      key: 'description',
      header: 'Description',
      render: (row: any) => row.description || 'N/A',
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (row: any) => row.amount ? `$${row.amount.toFixed(2)}` : 'N/A',
    },
    {
      key: 'receipt',
      header: 'Receipt',
      render: (row: any) => row.receipt_url ? (
        <Button size="sm" variant="ghost" onClick={() => window.open(row.receipt_url)}>
          <Upload className="h-4 w-4" />
        </Button>
      ) : 'No receipt',
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
              <Button size="sm" variant="ghost" onClick={() => handleApprove(row.id)} title="Approve">
                <CheckCircle className="h-4 w-4 text-green-600" />
              </Button>
              <Button size="sm" variant="ghost" onClick={() => handleReject(row.id)} title="Reject">
                <XCircle className="h-4 w-4 text-red-600" />
              </Button>
            </>
          )}
          <Button size="sm" variant="ghost" onClick={() => handleEdit(row)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleDelete(row.id)}>
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
        <p className="text-red-800">Error loading expenses: {error.message}</p>
      </div>
    )
  }

  const pendingCount = expenses.filter((e: any) => e.status === 'pending').length
  const approvedCount = expenses.filter((e: any) => e.status === 'approved').length
  const totalAmount = expenses.reduce((sum: number, e: any) => sum + (e.amount || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Expense Tracking</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => { setSelectedExpense(null); setIsModalOpen(true) }}>
            <Plus className="h-4 w-4 mr-2" />
            New Expense
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{expenses.length}</p>
              <p className="text-sm text-gray-600">Total Expenses</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{pendingCount}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{approvedCount}</p>
              <p className="text-sm text-gray-600">Approved</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">${totalAmount.toFixed(2)}</p>
              <p className="text-sm text-gray-600">Total Amount</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search expenses..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border rounded-lg"
            >
              <option value="">All Categories</option>
              <option value="travel">Travel</option>
              <option value="meals">Meals</option>
              <option value="supplies">Supplies</option>
              <option value="other">Other</option>
            </select>
          </div>
          <Table data={expenses} columns={columns} />
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
        title={selectedExpense ? 'Edit Expense' : 'New Expense'}
        size="lg"
      >
        <ExpenseForm
          initialData={selectedExpense}
          onSubmit={onSubmit}
          onCancel={() => {
            setIsModalOpen(false)
            setSelectedExpense(null)
          }}
          isLoading={isLoading}
        />
      </Modal>
    </div>
  )
}
