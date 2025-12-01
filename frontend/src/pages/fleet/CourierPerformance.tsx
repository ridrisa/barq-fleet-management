import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, Download, TrendingUp, TrendingDown, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { courierPerformanceAPI, couriersAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'

export default function CourierPerformance() {
  const { t: _t } = useTranslation()
  const [period, setPeriod] = useState('month')
  const [filterCourierId, setFilterCourierId] = useState('')
  const [couriers, setCouriers] = useState<any[]>([])
  const [isExporting, setIsExporting] = useState(false)

  // Load couriers for filter
  useEffect(() => {
    const loadCouriers = async () => {
      try {
        const data = await couriersAPI.getAll()
        setCouriers(data)
      } catch (error) {
        console.error('Failed to load couriers:', error)
      }
    }
    loadCouriers()
  }, [])

  // Calculate date range based on period
  const getDateRange = () => {
    const today = new Date()
    const startDate = new Date()

    switch (period) {
      case 'week':
        startDate.setDate(today.getDate() - 7)
        break
      case 'month':
        startDate.setMonth(today.getMonth() - 1)
        break
      case 'quarter':
        startDate.setMonth(today.getMonth() - 3)
        break
      case 'year':
        startDate.setFullYear(today.getFullYear() - 1)
        break
      default:
        startDate.setMonth(today.getMonth() - 1)
    }

    return {
      startDate: startDate.toISOString().split('T')[0],
      endDate: today.toISOString().split('T')[0],
    }
  }

  // Use the reusable data table hook
  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: performanceData,
    filteredData,
  } = useDataTable({
    queryKey: ['courierPerformance', period],
    queryFn: async () => {
      const { startDate, endDate } = getDateRange()
      return courierPerformanceAPI.getAll(0, 100, startDate, endDate)
    },
    pageSize: 10,
  })

  // Handle export to Excel
  const handleExport = async () => {
    setIsExporting(true)
    try {
      const { startDate, endDate } = getDateRange()
      const blob = await courierPerformanceAPI.exportToExcel(startDate, endDate)

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `courier-performance-${period}-${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export:', error)
    } finally {
      setIsExporting(false)
    }
  }

  // Filter by courier if selected
  const filteredBycourier = filterCourierId
    ? performanceData.filter((item: any) => String(item.courier_id) === filterCourierId)
    : performanceData

  // Calculate summary statistics
  const totalDeliveries = filteredBycourier.reduce((sum: number, item: any) => sum + (item.deliveries || 0), 0)
  const avgOnTimeRate = filteredBycourier.length > 0
    ? filteredBycourier.reduce((sum: number, item: any) => sum + (item.on_time_rate || 0), 0) / filteredBycourier.length
    : 0
  const avgRating = filteredBycourier.length > 0
    ? filteredBycourier.reduce((sum: number, item: any) => sum + (item.rating || 0), 0) / filteredBycourier.length
    : 0
  // Note: totalRevenue can be calculated if needed for future use
  // const totalRevenue = filteredBycourier.reduce((sum: number, item: any) => sum + (item.revenue || 0), 0)

  const getCourierName = (courierId: number) => {
    const courier = couriers.find((c) => c.id === courierId)
    return courier?.name || `Courier ${courierId}`
  }

  const columns = [
    {
      key: 'courier_id',
      header: 'Courier',
      sortable: true,
      render: (row: any) => (
        <div className="font-medium">
          {getCourierName(row.courier_id)}
        </div>
      ),
    },
    {
      key: 'deliveries',
      header: 'Deliveries',
      sortable: true,
      render: (row: any) => (
        <div className="font-semibold text-blue-600">
          {row.deliveries?.toLocaleString() || 0}
        </div>
      ),
    },
    {
      key: 'on_time_rate',
      header: 'On-Time Rate',
      sortable: true,
      render: (row: any) => {
        const rate = row.on_time_rate || 0
        const isGood = rate >= 95
        return (
          <div className="flex items-center gap-2">
            <span className={isGood ? 'text-green-600' : 'text-yellow-600'}>
              {rate.toFixed(1)}%
            </span>
            {isGood ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-yellow-600" />
            )}
          </div>
        )
      },
    },
    {
      key: 'rating',
      header: 'Rating',
      sortable: true,
      render: (row: any) => {
        const rating = row.rating || 0
        return (
          <div className="flex items-center gap-1">
            <span className="text-yellow-500">★</span>
            <span className="font-medium">{rating.toFixed(1)}</span>
            <span className="text-gray-400">/5</span>
          </div>
        )
      },
    },
    {
      key: 'cod_collected',
      header: 'COD Collected',
      sortable: true,
      render: (row: any) => (
        <span>SAR {(row.cod_collected || 0).toLocaleString()}</span>
      ),
    },
    {
      key: 'revenue',
      header: 'Revenue',
      sortable: true,
      render: (row: any) => (
        <span className="font-semibold text-green-600">
          SAR {(row.revenue || 0).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const onTimeRate = row.on_time_rate || 0
        const rating = row.rating || 0
        const isExcellent = onTimeRate >= 95 && rating >= 4.5
        const isGood = onTimeRate >= 90 && rating >= 4.0

        return (
          <Badge variant={isExcellent ? 'success' : isGood ? 'warning' : 'default'}>
            {isExcellent ? 'Excellent' : isGood ? 'Good' : 'Average'}
          </Badge>
        )
      },
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
        <p className="text-red-800">Error loading courier performance: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Courier Performance</h1>
        <div className="flex gap-2 items-center">
          <Calendar className="h-4 w-4 text-gray-400" />
          <Select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            options={[
              { value: 'week', label: 'This Week' },
              { value: 'month', label: 'This Month' },
              { value: 'quarter', label: 'This Quarter' },
              { value: 'year', label: 'This Year' },
            ]}
          />
          <Button variant="outline" onClick={handleExport} disabled={isExporting}>
            <Download className="h-4 w-4 mr-2" />
            {isExporting ? 'Exporting...' : 'Export'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {filteredBycourier.length}
              </p>
              <p className="text-sm text-gray-600">Active Couriers</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {totalDeliveries.toLocaleString()}
              </p>
              <p className="text-sm text-gray-600">Total Deliveries</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {avgOnTimeRate.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600">Avg On-Time Rate</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {avgRating.toFixed(1)}/5
              </p>
              <p className="text-sm text-gray-600">Avg Rating</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <div className="text-center text-gray-500">
              <TrendingUp className="h-12 w-12 mx-auto mb-2" />
              <p>Performance chart will be displayed here</p>
              <p className="text-sm">Showing trends for the selected period</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Rankings Table */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Rankings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search couriers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <Select
              value={filterCourierId}
              onChange={(e) => setFilterCourierId(e.target.value)}
              options={[
                { value: '', label: 'All Couriers' },
                ...couriers.map((c) => ({
                  value: String(c.id),
                  label: c.name,
                })),
              ]}
            />
          </div>
          <Table data={filteredBycourier} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Top Performers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Performers (By Deliveries)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {filteredBycourier
                .sort((a: any, b: any) => (b.deliveries || 0) - (a.deliveries || 0))
                .slice(0, 5)
                .map((courier: any, index: number) => (
                  <div key={courier.courier_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium">{getCourierName(courier.courier_id)}</p>
                        <p className="text-sm text-gray-600">{courier.deliveries} deliveries</p>
                      </div>
                    </div>
                    <Badge variant="success">
                      {courier.on_time_rate?.toFixed(1)}% on-time
                    </Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Rated Couriers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {filteredBycourier
                .sort((a: any, b: any) => (b.rating || 0) - (a.rating || 0))
                .slice(0, 5)
                .map((courier: any, index: number) => (
                  <div key={courier.courier_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-yellow-500 text-white flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium">{getCourierName(courier.courier_id)}</p>
                        <p className="text-sm text-gray-600">{courier.deliveries} deliveries</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">★</span>
                      <span className="font-bold">{courier.rating?.toFixed(1)}</span>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
