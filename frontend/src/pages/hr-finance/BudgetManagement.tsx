import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Download, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { budgetsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { BudgetForm } from '@/components/forms'

export default function BudgetManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedBudget, setSelectedBudget] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: budgets,
    filteredData,
  } = useDataTable({
    queryKey: 'budgets',
    queryFn: budgetsAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'budgets',
    entityName: 'Budget',
    create: budgetsAPI.create,
    update: budgetsAPI.update,
    delete: budgetsAPI.delete,
  })

  const handleEdit = (budget: any) => {
    setSelectedBudget(budget)
    setIsModalOpen(true)
  }

  const onSubmit = async (data: any) => {
    if (selectedBudget) {
      await handleUpdate(selectedBudget.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedBudget(null)
  }

  const columns = [
    {
      key: 'department',
      header: 'Department',
      sortable: true,
    },
    {
      key: 'allocated',
      header: 'Allocated',
      render: (row: any) => row.allocated ? `$${row.allocated.toFixed(2)}` : 'N/A',
    },
    {
      key: 'spent',
      header: 'Spent',
      render: (row: any) => row.spent ? `$${row.spent.toFixed(2)}` : 'N/A',
    },
    {
      key: 'remaining',
      header: 'Remaining',
      render: (row: any) => {
        const remaining = (row.allocated || 0) - (row.spent || 0)
        return `$${remaining.toFixed(2)}`
      },
    },
    {
      key: 'variance',
      header: 'Variance',
      render: (row: any) => {
        const variance = ((row.spent || 0) / (row.allocated || 1)) * 100
        const isOver = variance > 100
        return (
          <div className="flex items-center gap-2">
            {isOver ? (
              <TrendingUp className="h-4 w-4 text-red-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-green-600" />
            )}
            <span className={isOver ? 'text-red-600' : 'text-green-600'}>
              {variance.toFixed(1)}%
            </span>
          </div>
        )
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
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
        <p className="text-red-800">Error loading budgets: {error.message}</p>
      </div>
    )
  }

  const totalAllocated = budgets.reduce((sum: number, b: any) => sum + (b.allocated || 0), 0)
  const totalSpent = budgets.reduce((sum: number, b: any) => sum + (b.spent || 0), 0)
  const totalRemaining = totalAllocated - totalSpent

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Budget Management</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => { setSelectedBudget(null); setIsModalOpen(true) }}>
            <Plus className="h-4 w-4 mr-2" />
            New Budget
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">${totalAllocated.toFixed(2)}</p>
              <p className="text-sm text-gray-600">Total Allocated</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">${totalSpent.toFixed(2)}</p>
              <p className="text-sm text-gray-600">Total Spent</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">${totalRemaining.toFixed(2)}</p>
              <p className="text-sm text-gray-600">Remaining</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{budgets.length}</p>
              <p className="text-sm text-gray-600">Departments</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4">
            <Input
              placeholder="Search budgets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={budgets} columns={columns} />
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
        title={selectedBudget ? 'Edit Budget' : 'New Budget'}
        size="lg"
      >
        <BudgetForm
          initialData={selectedBudget}
          onSubmit={onSubmit}
          onCancel={() => {
            setIsModalOpen(false)
            setSelectedBudget(null)
          }}
          isLoading={isLoading}
        />
      </Modal>
    </div>
  )
}
