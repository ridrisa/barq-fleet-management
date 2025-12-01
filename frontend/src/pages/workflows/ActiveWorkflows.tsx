import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { workflowInstancesAPI } from '@/lib/api'
import { Search, Clock, User } from 'lucide-react'
import toast from 'react-hot-toast'

interface ActiveWorkflow {
  id: number
  template_name: string
  entity_type: string
  entity_id: number
  current_state: string
  status: 'pending' | 'in_progress'
  assigned_approver: string
  initiated_by: string
  started_at: string
  sla_deadline?: string
}

export default function ActiveWorkflows() {
  const [workflows, setWorkflows] = useState<ActiveWorkflow[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')

  useEffect(() => {
    loadWorkflows()
  }, [])

  const loadWorkflows = async () => {
    try {
      setLoading(true)
      const data = await workflowInstancesAPI.getAll()
      const activeData = data.filter(
        (w: any) => w.status === 'pending' || w.status === 'in_progress'
      )
      setWorkflows(activeData)
    } catch (error) {
      toast.error('Failed to load active workflows')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.template_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workflow.assigned_approver.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || workflow.status === statusFilter
    const matchesType = typeFilter === 'all' || workflow.entity_type === typeFilter

    return matchesSearch && matchesStatus && matchesType
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const isOverdue = (deadline?: string) => {
    if (!deadline) return false
    return new Date(deadline) < new Date()
  }

  const getEntityTypes = () => {
    const types = new Set(workflows.map(w => w.entity_type))
    return Array.from(types)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Active Workflows</h1>
        <Badge className="bg-blue-100 text-blue-800 text-lg px-4 py-2">
          {filteredWorkflows.length} Active
        </Badge>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search workflows or approvers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="w-48">
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
              </Select>
            </div>

            <div className="w-48">
              <Select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <option value="all">All Types</option>
                {getEntityTypes().map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredWorkflows.map((workflow) => (
          <Card key={workflow.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{workflow.template_name}</h3>
                    <Badge className={
                      workflow.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }>
                      {workflow.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                    {workflow.sla_deadline && isOverdue(workflow.sla_deadline) && (
                      <Badge className="bg-red-100 text-red-800">
                        SLA OVERDUE
                      </Badge>
                    )}
                  </div>

                  <p className="text-sm text-gray-600 mb-3">
                    {workflow.entity_type} #{workflow.entity_id}
                  </p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="flex items-center gap-1 text-gray-600 mb-1">
                        <User className="h-3 w-3" />
                        <span>Assigned To</span>
                      </div>
                      <p className="font-medium">{workflow.assigned_approver}</p>
                    </div>

                    <div>
                      <div className="text-gray-600 mb-1">Initiated By</div>
                      <p className="font-medium">{workflow.initiated_by}</p>
                    </div>

                    <div>
                      <div className="flex items-center gap-1 text-gray-600 mb-1">
                        <Clock className="h-3 w-3" />
                        <span>Started</span>
                      </div>
                      <p className="font-medium">{formatDate(workflow.started_at)}</p>
                    </div>

                    <div>
                      <div className="text-gray-600 mb-1">Current State</div>
                      <p className="font-medium">{workflow.current_state}</p>
                    </div>
                  </div>

                  {workflow.sla_deadline && (
                    <div className="mt-3 pt-3 border-t">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">SLA Deadline:</span>
                        <span className={`font-medium ${isOverdue(workflow.sla_deadline) ? 'text-red-600' : 'text-gray-900'}`}>
                          {formatDate(workflow.sla_deadline)}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredWorkflows.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-gray-500">
            {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
              ? 'No workflows match your filters.'
              : 'No active workflows at the moment.'}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
