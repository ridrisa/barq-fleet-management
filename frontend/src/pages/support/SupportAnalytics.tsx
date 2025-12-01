import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { supportAnalyticsAPI } from '@/lib/api'
import { exportToExcel, exportToPDF } from '@/lib/export'
import {
  FileSpreadsheet,
  FileText,
  Ticket,
  Clock,
  CheckCircle,
  TrendingUp,
} from 'lucide-react'
import toast from 'react-hot-toast'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'


const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function SupportAnalytics() {
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
  })

  // Fetch analytics data
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['support-analytics-summary', dateRange],
    queryFn: () => supportAnalyticsAPI.getSummary(dateRange.startDate, dateRange.endDate),
  })

  const { data: ticketsOverTime, isLoading: ticketsLoading } = useQuery({
    queryKey: ['support-tickets-over-time', dateRange],
    queryFn: () => supportAnalyticsAPI.getTicketsOverTime(dateRange.startDate, dateRange.endDate),
  })

  const { data: ticketsByCategory, isLoading: categoryLoading } = useQuery({
    queryKey: ['support-tickets-by-category', dateRange],
    queryFn: () => supportAnalyticsAPI.getTicketsByCategory(dateRange.startDate, dateRange.endDate),
  })

  const { data: resolutionTime, isLoading: resolutionLoading } = useQuery({
    queryKey: ['support-resolution-time', dateRange],
    queryFn: () => supportAnalyticsAPI.getResolutionTimeByCategory(dateRange.startDate, dateRange.endDate),
  })

  const { data: commonIssues, isLoading: issuesLoading } = useQuery({
    queryKey: ['support-common-issues', dateRange],
    queryFn: () => supportAnalyticsAPI.getCommonIssues(dateRange.startDate, dateRange.endDate),
  })

  const isLoading = summaryLoading || ticketsLoading || categoryLoading || resolutionLoading || issuesLoading

  const handleExportExcel = () => {
    const data = [
      { metric: 'Total Tickets', value: summary?.totalTickets },
      { metric: 'Open Tickets', value: summary?.openTickets },
      { metric: 'Avg Resolution Time (hours)', value: summary?.avgResolutionTime },
      { metric: 'Customer Satisfaction', value: summary?.customerSatisfaction },
    ]
    exportToExcel(data, 'support-analytics')
    toast.success('Exported to Excel')
  }

  const handleExportPDF = async () => {
    await exportToPDF('analytics-content', 'support-analytics')
    toast.success('Exported to PDF')
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  const summaryCards = [
    {
      title: 'Total Tickets',
      value: summary?.totalTickets || 0,
      icon: Ticket,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Open Tickets',
      value: summary?.openTickets || 0,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'Avg Resolution Time',
      value: `${summary?.avgResolutionTime || 0}h`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Customer Satisfaction',
      value: `${summary?.customerSatisfaction || 0}%`,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ]

  return (
    <div className="space-y-6" id="analytics-content">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Support Analytics</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportExcel}>
            <FileSpreadsheet className="w-4 h-4 mr-2" />
            Export Excel
          </Button>
          <Button variant="outline" onClick={handleExportPDF}>
            <FileText className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Date Range Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Start Date</label>
              <Input
                type="date"
                value={dateRange.startDate}
                onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">End Date</label>
              <Input
                type="date"
                value={dateRange.endDate}
                onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {summaryCards.map((card) => (
          <Card key={card.title}>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold mt-2">{card.value}</p>
                </div>
                <div className={`p-3 rounded-full ${card.bgColor}`}>
                  <card.icon className={`w-6 h-6 ${card.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tickets Over Time */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold mb-4">Tickets Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={ticketsOverTime || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="tickets" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Tickets by Category */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Tickets by Category</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={ticketsByCategory || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {(ticketsByCategory || []).map((_entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Resolution Time by Category */}
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Resolution Time by Category (hours)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={resolutionTime || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avgTime" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top 10 Common Issues */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold mb-4">Top 10 Common Issues</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={commonIssues || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="issue" type="category" width={150} />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
