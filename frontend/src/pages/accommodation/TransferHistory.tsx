import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { Pagination } from '@/components/ui/Pagination'
import { bedAssignmentsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { exportToExcel } from '@/lib/export'
import { Download, Search, ArrowRight, Calendar } from 'lucide-react'

interface Transfer {
  id: number
  courier_name: string
  from_building: string
  from_room: string
  from_bed: string
  to_building: string
  to_room: string
  to_bed: string
  transfer_date: string
  reason: string
  requested_by: string
  approved_by: string
  status: 'pending' | 'approved' | 'completed' | 'rejected'
}

export default function TransferHistory() {
  const [dateRange, setDateRange] = useState({ from: '', to: '' })

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
    paginatedData: transfers,
  } = useDataTable({
    queryKey: 'transfer-history',
    queryFn: async () => {
      try {
        const assignments = await bedAssignmentsAPI.getAll()
        // Transform bed assignments to transfer history format
        return assignments.map((a: any, index: number) => ({
          id: a.id || index + 1,
          courier_name: a.courier_name || `Courier ${a.courier_id}`,
          from_building: a.previous_building || 'N/A',
          from_room: a.previous_room || 'N/A',
          from_bed: a.previous_bed || 'N/A',
          to_building: a.building_name || a.building || 'N/A',
          to_room: a.room_number || a.room || 'N/A',
          to_bed: a.bed_number || a.bed || 'N/A',
          transfer_date: a.assigned_date || a.created_at || new Date().toISOString(),
          reason: a.reason || a.notes || 'Standard assignment',
          requested_by: a.requested_by || 'System',
          approved_by: a.approved_by || 'Manager',
          status: a.status || 'completed',
        }))
      } catch (err) {
        console.error('Error fetching transfers:', err)
        return []
      }
    },
    pageSize: 10,
  })

  const getStatusColor = (status: Transfer['status']) => {
    const colors = {
      pending: 'warning',
      approved: 'primary',
      completed: 'success',
      rejected: 'error',
    }
    return colors[status] as 'warning' | 'primary' | 'success' | 'error'
  }

  // Apply date filter
  const displayData = (filteredData as Transfer[]).filter((transfer) => {
    if (!dateRange.from && !dateRange.to) return true
    const transferDate = new Date(transfer.transfer_date)
    const fromDate = dateRange.from ? new Date(dateRange.from) : new Date(0)
    const toDate = dateRange.to ? new Date(dateRange.to) : new Date()
    return transferDate >= fromDate && transferDate <= toDate
  })

  const handleExport = () => {
    const exportData = displayData.map((t: Transfer) => ({
      'Courier': t.courier_name,
      'From Building': t.from_building,
      'From Room': t.from_room,
      'From Bed': t.from_bed,
      'To Building': t.to_building,
      'To Room': t.to_room,
      'To Bed': t.to_bed,
      'Transfer Date': t.transfer_date,
      'Reason': t.reason,
      'Status': t.status,
    }))
    exportToExcel(exportData, `transfer-history-${new Date().toISOString().split('T')[0]}`)
  }

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
        <p className="text-red-800">Error loading transfer history: {(error as Error).message}</p>
      </div>
    )
  }

  // Summary stats
  const typedData = filteredData as Transfer[]
  const stats = {
    total: typedData.length,
    completed: typedData.filter((t) => t.status === 'completed').length,
    pending: typedData.filter((t) => t.status === 'pending').length,
    rejected: typedData.filter((t) => t.status === 'rejected').length,
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transfer History</h1>
        <Button onClick={handleExport}>
          <Download className="h-4 w-4 mr-2" />
          Export to Excel
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
              <p className="text-sm text-gray-600">Total Transfers</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
              <p className="text-sm text-gray-600">Rejected</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transfer Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Input
              placeholder="Search courier or building..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
            <Input
              type="date"
              placeholder="From Date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
            />
            <Input
              type="date"
              placeholder="To Date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
            />
          </div>

          <div className="space-y-4">
            {transfers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No transfer records found
              </div>
            ) : (
              (transfers as Transfer[]).map((transfer) => (
                <Card key={transfer.id} className="border-l-4 border-blue-500">
                  <CardContent className="pt-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{transfer.courier_name}</h3>
                        <p className="text-sm text-gray-600">
                          {new Date(transfer.transfer_date).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge variant={getStatusColor(transfer.status)}>
                        {transfer.status}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-4 mb-3">
                      <div className="flex-1 p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">From</p>
                        <p className="font-medium">
                          {transfer.from_building} - Room {transfer.from_room}, Bed {transfer.from_bed}
                        </p>
                      </div>
                      <ArrowRight className="h-5 w-5 text-blue-600 flex-shrink-0" />
                      <div className="flex-1 p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">To</p>
                        <p className="font-medium">
                          {transfer.to_building} - Room {transfer.to_room}, Bed {transfer.to_bed}
                        </p>
                      </div>
                    </div>

                    <div className="mb-3">
                      <p className="text-xs text-gray-500 mb-1">Reason</p>
                      <p className="text-sm">{transfer.reason}</p>
                    </div>

                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Requested by: {transfer.requested_by}</span>
                      <span>Approved by: {transfer.approved_by}</span>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>

          <div className="mt-4">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={displayData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
