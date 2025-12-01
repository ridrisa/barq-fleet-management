import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'

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
  const [transfers, setTransfers] = useState<Transfer[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [dateRange, setDateRange] = useState({ from: '', to: '' })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      // Mock data
      const mockTransfers: Transfer[] = [
        {
          id: 1,
          courier_name: 'Ahmed Ali',
          from_building: 'Marina Tower',
          from_room: '301',
          from_bed: 'A',
          to_building: 'Downtown Residence',
          to_room: '101',
          to_bed: 'A',
          transfer_date: '2024-01-15',
          reason: 'Requested room change - closer to workplace',
          requested_by: 'Ahmed Ali',
          approved_by: 'Manager 1',
          status: 'completed',
        },
        {
          id: 2,
          courier_name: 'Mohammed Hassan',
          from_building: 'Downtown Residence',
          from_room: '102',
          from_bed: 'B',
          to_building: 'Marina Tower',
          to_room: '305',
          to_bed: 'A',
          transfer_date: '2024-02-10',
          reason: 'Room maintenance required',
          requested_by: 'Manager 1',
          approved_by: 'Manager 1',
          status: 'completed',
        },
        {
          id: 3,
          courier_name: 'Fatima Ahmed',
          from_building: 'Downtown Residence',
          from_room: '103',
          from_bed: 'C',
          to_building: 'Marina Tower',
          to_room: '302',
          to_bed: 'B',
          transfer_date: '2024-03-05',
          reason: 'Personal preference',
          requested_by: 'Fatima Ahmed',
          approved_by: 'Pending',
          status: 'pending',
        },
      ]
      setTransfers(mockTransfers)
    } catch (error) {
      console.error('Failed to fetch transfers:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: Transfer['status']) => {
    const colors = {
      pending: 'warning',
      approved: 'primary',
      completed: 'success',
      rejected: 'error',
    }
    return colors[status] as 'warning' | 'primary' | 'success' | 'error'
  }

  const filteredTransfers = transfers.filter((transfer) => {
    const matchesSearch =
      transfer.courier_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transfer.from_building.toLowerCase().includes(searchTerm.toLowerCase()) ||
      transfer.to_building.toLowerCase().includes(searchTerm.toLowerCase())

    return matchesSearch
  })

  const exportToExcel = () => {
    console.log('Exporting to Excel...', filteredTransfers)
    // In real implementation, use a library like xlsx or csv-writer
    alert('Export functionality would download Excel file here')
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transfer History</h1>
        <Button onClick={exportToExcel}>Export to Excel</Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Input
              placeholder="Search courier or building..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <input
              type="date"
              className="px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="From Date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
            />
            <input
              type="date"
              className="px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="To Date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
            />
          </div>

          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-4">
              {filteredTransfers.map((transfer) => (
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

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                      <div>
                        <p className="text-xs text-gray-500 mb-1">From</p>
                        <p className="font-medium">
                          {transfer.from_building} - Room {transfer.from_room}, Bed{' '}
                          {transfer.from_bed}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 mb-1">To</p>
                        <p className="font-medium">
                          {transfer.to_building} - Room {transfer.to_room}, Bed{' '}
                          {transfer.to_bed}
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
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
