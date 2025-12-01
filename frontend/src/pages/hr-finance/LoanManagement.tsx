import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Download, FileText } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { loansAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { LoanForm, LoanFormData } from '@/components/forms/LoanForm'

export default function LoanManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedLoan, setSelectedLoan] = useState<any>(null)
  const [showSchedule, setShowSchedule] = useState(false)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: loans,
    filteredData,
  } = useDataTable({
    queryKey: 'loans',
    queryFn: loansAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'loans',
    entityName: 'Loan',
    create: loansAPI.create,
    update: loansAPI.update,
    delete: loansAPI.delete,
  })

  const handleEdit = (loan: any) => {
    setSelectedLoan(loan)
    setIsModalOpen(true)
  }

  const handleViewSchedule = (loan: any) => {
    setSelectedLoan(loan)
    setShowSchedule(true)
  }

  const handleFormSubmit = async (data: LoanFormData) => {
    if (selectedLoan) {
      await handleUpdate(selectedLoan.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedLoan(null)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedLoan(null)
  }

  const columns = [
    {
      key: 'courier_name',
      header: 'Courier Name',
      sortable: true,
    },
    {
      key: 'amount',
      header: 'Loan Amount',
      render: (row: any) => row.amount ? `$${row.amount.toFixed(2)}` : 'N/A',
    },
    {
      key: 'monthly_payment',
      header: 'Monthly Payment',
      render: (row: any) => row.monthly_payment ? `$${row.monthly_payment.toFixed(2)}` : 'N/A',
    },
    {
      key: 'remaining',
      header: 'Remaining',
      render: (row: any) => row.remaining ? `$${row.remaining.toFixed(2)}` : 'N/A',
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
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'active'
              ? 'success'
              : row.status === 'completed'
              ? 'default'
              : row.status === 'pending'
              ? 'warning'
              : 'danger'
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
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleViewSchedule(row)}
            title="View Schedule"
          >
            <FileText className="h-4 w-4" />
          </Button>
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
          Error loading loans: {error.message}
        </p>
      </div>
    )
  }

  const activeLoans = loans.filter((l: any) => l.status === 'active').length
  const totalAmount = loans.reduce((sum: number, l: any) => sum + (l.amount || 0), 0)
  const totalRemaining = loans.reduce((sum: number, l: any) => sum + (l.remaining || 0), 0)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Loan Management</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={() => { setSelectedLoan(null); setIsModalOpen(true) }}>
            <Plus className="h-4 w-4 mr-2" />
            New Loan
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {loans.length}
              </p>
              <p className="text-sm text-gray-600">Total Loans</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {activeLoans}
              </p>
              <p className="text-sm text-gray-600">Active</p>
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
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                ${totalRemaining.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600">Total Remaining</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4">
            <Input
              placeholder="Search loans..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={loans} columns={columns} />
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
        title={selectedLoan ? 'Edit Loan' : 'New Loan'}
        size="lg"
      >
        <LoanForm
          initialData={selectedLoan}
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          mode={selectedLoan ? 'edit' : 'create'}
        />
      </Modal>

      <Modal
        isOpen={showSchedule}
        onClose={() => setShowSchedule(false)}
        title="Repayment Schedule"
        size="lg"
      >
        <p>Repayment schedule will be displayed here</p>
      </Modal>
    </div>
  )
}
