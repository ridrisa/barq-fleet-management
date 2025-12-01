import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { TrendingUp, TrendingDown, Clock, Download, Calendar, Target, Award } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Spinner } from '@/components/ui/Spinner'
import { KPICard } from '@/components/ui/KPICard'
import { courierPerformanceAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'

export default function PerformanceTracking() {
  useTranslation()
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const {
    isLoading,
    error,
    paginatedData: performance,
    filteredData,
  } = useDataTable({
    queryKey: ['courier-performance', startDate, endDate],
    queryFn: () => courierPerformanceAPI.getAll(0, 100, startDate, endDate),
    pageSize: 10,
  })

  const handleExport = async () => {
    try {
      const blob = await courierPerformanceAPI.exportToExcel(startDate, endDate)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `performance-${new Date().toISOString().split('T')[0]}.xlsx`
      link.click()
    } catch (error) {
      alert('Export feature will be implemented soon!')
    }
  }

  // Calculate stats
  const stats = {
    totalDeliveries: filteredData.reduce((sum: number, p: any) => sum + (p.deliveries || 0), 0),
    avgSuccessRate: filteredData.length > 0
      ? filteredData.reduce((sum: number, p: any) => sum + (p.success_rate || 0), 0) / filteredData.length
      : 0,
    avgRating: filteredData.length > 0
      ? filteredData.reduce((sum: number, p: any) => sum + (p.rating || 0), 0) / filteredData.length
      : 0,
    avgTime: filteredData.length > 0
      ? filteredData.reduce((sum: number, p: any) => sum + (p.avg_time || 0), 0) / filteredData.length
      : 0,
  }

  const columns = [
    {
      key: 'courier_name',
      header: 'Courier',
      sortable: true,
      render: (row: any) => (
        <div className="font-semibold text-gray-900">
          {row.courier_name || `Courier #${row.courier_id}`}
        </div>
      ),
    },
    {
      key: 'deliveries',
      header: 'Deliveries',
      render: (row: any) => row.deliveries || 0,
    },
    {
      key: 'success_rate',
      header: 'Success Rate',
      render: (row: any) => {
        const rate = row.success_rate || 0
        return (
          <div className="flex items-center gap-2">
            <span className={`font-semibold ${rate >= 90 ? 'text-green-600' : rate >= 75 ? 'text-yellow-600' : 'text-red-600'}`}>
              {rate.toFixed(1)}%
            </span>
            {rate >= 90 && <TrendingUp className="h-4 w-4 text-green-600" />}
            {rate < 75 && <TrendingDown className="h-4 w-4 text-red-600" />}
          </div>
        )
      },
    },
    {
      key: 'avg_time',
      header: 'Avg Time',
      render: (row: any) => `${row.avg_time || 0}m`,
    },
    {
      key: 'rating',
      header: 'Rating',
      render: (row: any) => {
        const rating = row.rating || 0
        return (
          <div className="flex items-center gap-1">
            <span className="text-yellow-500">★</span>
            <span className="font-semibold">{rating.toFixed(1)}</span>
          </div>
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
        <p className="text-red-800">Error loading performance data: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Performance Tracking</h1>
        <Button variant="outline" onClick={handleExport}>
          <Download className="h-4 w-4 mr-2" />
          Export Report
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Deliveries"
          value={stats.totalDeliveries}
          icon={<Target className="h-6 w-6" />}
          color="blue"
          loading={isLoading}
        />
        <KPICard
          title="Avg Success Rate"
          value={`${stats.avgSuccessRate.toFixed(1)}%`}
          icon={<TrendingUp className="h-6 w-6" />}
          color="green"
          trend={stats.avgSuccessRate >= 85 ? 'up' : 'down'}
          loading={isLoading}
        />
        <KPICard
          title="Avg Rating"
          value={stats.avgRating.toFixed(1)}
          icon={<Award className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
        <KPICard
          title="Avg Time"
          value={`${Math.floor(stats.avgTime)}m`}
          icon={<Clock className="h-6 w-6" />}
          color="indigo"
          loading={isLoading}
        />
      </div>

      {/* Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Courier Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="w-full sm:w-48">
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  placeholder="Start Date"
                  leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-48">
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  placeholder="End Date"
                  leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
                />
              </div>
            </div>

            <Table data={performance} columns={columns} />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
