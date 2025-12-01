import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Badge } from '@/components/ui/Badge'
import { Table } from '@/components/ui/Table'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { Pagination } from '@/components/ui/Pagination'
import { ticketsAPI } from '@/lib/api'
import { exportToExcel, exportToCSV } from '@/lib/export'
import { Plus, FileSpreadsheet, FileText, Search, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'

type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed'
type TicketPriority = 'low' | 'medium' | 'high' | 'urgent'

interface Ticket {
  id: number
  title: string
  description: string
  status: TicketStatus
  priority: TicketPriority
  category: string
  created_by: string
  assigned_to?: string
  created_at: string
  updated_at: string
}

export default function Tickets() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [limit] = useState(20)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'medium' as TicketPriority,
  })

  // Fetch tickets
  const { data, isLoading, error } = useQuery({
    queryKey: ['tickets', page, limit, statusFilter, priorityFilter],
    queryFn: () =>
      ticketsAPI.getAll((page - 1) * limit, limit, {
        status: statusFilter !== 'all' ? statusFilter : undefined,
        priority: priorityFilter !== 'all' ? priorityFilter : undefined,
      }),
  })

  // Create ticket mutation
  const createMutation = useMutation({
    mutationFn: ticketsAPI.create,
    onSuccess: () => {
      toast.success('Ticket created successfully')
      queryClient.invalidateQueries({ queryKey: ['tickets'] })
      setShowCreateModal(false)
      resetForm()
    },
    onError: () => {
      toast.error('Failed to create ticket')
    },
  })

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: '',
      priority: 'medium',
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title || !formData.description || !formData.category) {
      toast.error('Please fill all required fields')
      return
    }
    createMutation.mutate(formData)
  }

  const handleExportExcel = () => {
    if (data?.tickets) {
      exportToExcel(data.tickets, 'support-tickets')
      toast.success('Exported to Excel')
    }
  }

  const handleExportCSV = () => {
    if (data?.tickets) {
      exportToCSV(data.tickets, 'support-tickets')
      toast.success('Exported to CSV')
    }
  }

  const getStatusBadge = (status: TicketStatus) => {
    const variants: Record<TicketStatus, 'default' | 'success' | 'warning' | 'error'> = {
      open: 'default',
      in_progress: 'warning',
      resolved: 'success',
      closed: 'default',
    }
    return <Badge variant={variants[status]}>{status.replace('_', ' ')}</Badge>
  }

  const getPriorityBadge = (priority: TicketPriority) => {
    const variants: Record<TicketPriority, 'default' | 'success' | 'warning' | 'error'> = {
      low: 'success',
      medium: 'default',
      high: 'warning',
      urgent: 'error',
    }
    return <Badge variant={variants[priority]}>{priority}</Badge>
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
      <div className="text-center text-red-600">
        Error loading tickets: {(error as Error).message}
      </div>
    )
  }

  const tickets = data?.tickets || []
  const total = data?.total || 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Support Tickets</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
          <Button variant="outline" onClick={handleExportCSV}>
            <FileText className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={handleExportExcel}>
            <FileSpreadsheet className="w-4 h-4 mr-2" />
            Export Excel
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Ticket
          </Button>
        </div>
      </div>

      {showFilters && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Search</label>
                <Input
                  placeholder="Search tickets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  icon={<Search className="w-4 h-4" />}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Statuses' },
                    { value: 'open', label: 'Open' },
                    { value: 'in_progress', label: 'In Progress' },
                    { value: 'resolved', label: 'Resolved' },
                    { value: 'closed', label: 'Closed' },
                  ]}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Priority</label>
                <Select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Priorities' },
                    { value: 'low', label: 'Low' },
                    { value: 'medium', label: 'Medium' },
                    { value: 'high', label: 'High' },
                    { value: 'urgent', label: 'Urgent' },
                  ]}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          {tickets.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No tickets found</p>
              <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                Create your first ticket
              </Button>
            </div>
          ) : (
            <>
              <Table
                columns={[
                  { key: 'id', label: 'ID' },
                  { key: 'title', label: 'Title' },
                  { key: 'category', label: 'Category' },
                  {
                    key: 'status',
                    label: 'Status',
                    render: (ticket: Ticket) => getStatusBadge(ticket.status),
                  },
                  {
                    key: 'priority',
                    label: 'Priority',
                    render: (ticket: Ticket) => getPriorityBadge(ticket.priority),
                  },
                  { key: 'created_by', label: 'Created By' },
                  { key: 'assigned_to', label: 'Assigned To' },
                  {
                    key: 'created_at',
                    label: 'Created',
                    render: (ticket: Ticket) =>
                      new Date(ticket.created_at).toLocaleDateString(),
                  },
                ]}
                data={tickets}
                onRowClick={(ticket) => navigate(`/support/tickets/${ticket.id}`)}
              />

              <div className="mt-4">
                <Pagination
                  currentPage={page}
                  totalPages={Math.ceil(total / limit)}
                  onPageChange={setPage}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Create Ticket Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Support Ticket"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Brief description of the issue"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Description <span className="text-red-500">*</span>
            </label>
            <textarea
              className="w-full border rounded-md p-2 min-h-[100px]"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Detailed description of the issue"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <Select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              options={[
                { value: '', label: 'Select Category' },
                { value: 'technical', label: 'Technical Issue' },
                { value: 'billing', label: 'Billing' },
                { value: 'feature', label: 'Feature Request' },
                { value: 'bug', label: 'Bug Report' },
                { value: 'other', label: 'Other' },
              ]}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Priority</label>
            <Select
              value={formData.priority}
              onChange={(e) =>
                setFormData({ ...formData, priority: e.target.value as TicketPriority })
              }
              options={[
                { value: 'low', label: 'Low' },
                { value: 'medium', label: 'Medium' },
                { value: 'high', label: 'High' },
                { value: 'urgent', label: 'Urgent' },
              ]}
            />
          </div>

          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Ticket'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
