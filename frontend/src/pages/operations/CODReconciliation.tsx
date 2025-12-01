import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, DollarSign, CheckCircle, Clock, Filter, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { Checkbox } from '@/components/forms/Checkbox'
import { codAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

export default function CODReconciliation() {
  const { t: _t } = useTranslation()
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedIds, setSelectedIds] = useState<number[]>([])

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
  } = useDataTable({
    queryKey: 'cod-reconciliation',
    queryFn: codAPI.getAll,
    pageSize: 15,
  })

  const { handleUpdate } = useCRUD({
    queryKey: 'cod-reconciliation',
    entityName: 'COD Record',
    create: codAPI.create,
    update: codAPI.update,
    delete: codAPI.delete,
  })

  // Filter by status
  const statusFilteredData = statusFilter === 'all'
    ? filteredData
    : filteredData.filter((c: any) => {
        if (statusFilter === 'reconciled') return c.is_reconciled || c.reconciled
        if (statusFilter === 'pending') return !c.is_reconciled && !c.reconciled
        return true
      })

  // Calculate summary stats
  const stats = {
    totalCOD: filteredData.reduce((sum: number, record: any) =>
      sum + (record.amount_collected || record.amount || 0), 0
    ),
    reconciled: filteredData
      .filter((r: any) => r.is_reconciled || r.reconciled)
      .reduce((sum: number, record: any) => sum + (record.amount_collected || record.amount || 0), 0),
    pending: filteredData
      .filter((r: any) => !r.is_reconciled && !r.reconciled)
      .reduce((sum: number, record: any) => sum + (record.amount_collected || record.amount || 0), 0),
    count: filteredData.length,
  }

  const handleSelectAll = () => {
    if (selectedIds.length === statusFilteredData.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(statusFilteredData.map((r: any) => r.id))
    }
  }

  const handleSelectOne = (id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const handleBulkReconcile = async () => {
    if (selectedIds.length === 0) {
      alert('Please select records to reconcile')
      return
    }

    if (window.confirm(`Reconcile ${selectedIds.length} COD records?`)) {
      for (const id of selectedIds) {
        await handleUpdate(id, { is_reconciled: true, reconciled: true, reconciled_at: new Date().toISOString() })
      }
      setSelectedIds([])
    }
  }

  const handleExport = () => {
    alert('Exporting COD reconciliation report to Excel...')
  }

  const columns = [
    {
      key: 'select',
      header: (
        <Checkbox
          checked={selectedIds.length === statusFilteredData.length && statusFilteredData.length > 0}
          onChange={handleSelectAll}
        />
      ),
      render: (row: any) => (
        <Checkbox
          checked={selectedIds.includes(row.id)}
          onChange={() => handleSelectOne(row.id)}
        />
      ),
    },
    {
      key: 'delivery_id',
      header: 'Delivery ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.tracking_number || `DEL-${row.delivery_id?.toString().padStart(6, '0')}`}
        </div>
      ),
    },
    {
      key: 'courier_id',
      header: 'Courier',
      render: (row: any) => row.courier_name || `Courier #${row.courier_id || 'N/A'}`,
    },
    {
      key: 'amount_collected',
      header: 'Amount',
      render: (row: any) => {
        const amount = row.amount_collected || row.amount || 0
        return (
          <span className="font-semibold text-green-600">
            ${amount.toFixed(2)}
          </span>
        )
      },
    },
    {
      key: 'collection_date',
      header: 'Collection Date',
      render: (row: any) => {
        const date = row.collection_date || row.collected_at || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'is_reconciled',
      header: 'Status',
      render: (row: any) => {
        const reconciled = row.is_reconciled || row.reconciled
        return (
          <Badge variant={reconciled ? 'success' : 'warning'}>
            {reconciled ? 'Reconciled' : 'Pending'}
          </Badge>
        )
      },
    },
    {
      key: 'reconciled_at',
      header: 'Reconciled Date',
      render: (row: any) => {
        const date = row.reconciled_at || row.reconciliation_date
        return date ? new Date(date).toLocaleDateString() : '-'
      },
    },
    {
      key: 'notes',
      header: 'Notes',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.notes || '-'}
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
        <p className="text-red-800">Error loading COD records: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">COD Reconciliation</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          {selectedIds.length > 0 && (
            <Button onClick={handleBulkReconcile}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Reconcile ({selectedIds.length})
            </Button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total COD</p>
                <p className="text-2xl font-bold text-gray-900">${stats.totalCOD.toFixed(2)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Reconciled</p>
                <p className="text-2xl font-bold text-green-600">${stats.reconciled.toFixed(2)}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-orange-600">${stats.pending.toFixed(2)}</p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Records</p>
                <p className="text-2xl font-bold text-gray-900">{stats.count}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                <span className="text-gray-600 text-xl">#</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* COD Records Table */}
      <Card>
        <CardHeader>
          <CardTitle>COD Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by delivery ID, courier..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-48">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Status' },
                    { value: 'reconciled', label: 'Reconciled' },
                    { value: 'pending', label: 'Pending' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
            </div>

            <Table
              data={statusFilteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)}
              columns={columns}
            />

            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(statusFilteredData.length / pageSize)}
              onPageChange={setCurrentPage}
              totalItems={statusFilteredData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
