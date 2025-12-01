import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Search, Download, FileText, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'

interface WorkflowHistory {
  id: number
  workflow_name: string
  entity_type: string
  entity_id: number
  status: 'approved' | 'rejected' | 'cancelled'
  initiated_by: string
  started_at: string
  completed_at: string
  approver: string
  comment?: string
  audit_trail: {
    step: string
    user: string
    action: string
    timestamp: string
  }[]
}

export default function History() {
  const [histories] = useState<WorkflowHistory[]>([
    {
      id: 1,
      workflow_name: 'Leave Request',
      entity_type: 'Leave',
      entity_id: 100,
      status: 'approved',
      initiated_by: 'John Doe',
      started_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      completed_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      approver: 'Jane Smith',
      comment: 'Approved - sufficient leave balance',
      audit_trail: [
        { step: 'Submitted', user: 'John Doe', action: 'Created request', timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString() },
        { step: 'Supervisor Review', user: 'Jane Smith', action: 'Approved', timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() }
      ]
    },
    {
      id: 2,
      workflow_name: 'Vehicle Assignment',
      entity_type: 'Assignment',
      entity_id: 200,
      status: 'rejected',
      initiated_by: 'Mike Johnson',
      started_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      completed_at: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
      approver: 'Sarah Brown',
      comment: 'Vehicle already assigned to another courier',
      audit_trail: [
        { step: 'Submitted', user: 'Mike Johnson', action: 'Created request', timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString() },
        { step: 'Manager Review', user: 'Sarah Brown', action: 'Rejected', timestamp: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString() }
      ]
    }
  ])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredHistories = histories.filter(history => {
    const matchesSearch = history.workflow_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         history.initiated_by.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || history.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'approved':
        return { color: 'bg-green-100 text-green-800', icon: CheckCircle }
      case 'rejected':
        return { color: 'bg-red-100 text-red-800', icon: XCircle }
      case 'cancelled':
        return { color: 'bg-gray-100 text-gray-800', icon: XCircle }
      default:
        return { color: 'bg-gray-100 text-gray-800', icon: FileText }
    }
  }

  const exportToPDF = (history: WorkflowHistory) => {
    console.log('Exporting to PDF:', history)
    toast.success('PDF export started')
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow History</h1>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search workflows..."
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
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="cancelled">Cancelled</option>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {filteredHistories.map((history) => {
          const statusConfig = getStatusConfig(history.status)
          const StatusIcon = statusConfig.icon

          return (
            <Card key={history.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{history.workflow_name}</h3>
                      <Badge className={statusConfig.color}>
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {history.status.toUpperCase()}
                      </Badge>
                    </div>

                    <p className="text-sm text-gray-600 mb-3">
                      {history.entity_type} #{history.entity_id}
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-600">Initiated By:</span>
                        <p className="font-medium">{history.initiated_by}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Started:</span>
                        <p className="font-medium">{formatDate(history.started_at)}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Completed:</span>
                        <p className="font-medium">{formatDate(history.completed_at)}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Final Approver:</span>
                        <p className="font-medium">{history.approver}</p>
                      </div>
                    </div>

                    {history.comment && (
                      <div className="p-3 bg-gray-50 rounded-lg mb-4">
                        <p className="text-sm font-semibold text-gray-700 mb-1">Comment:</p>
                        <p className="text-sm text-gray-600">{history.comment}</p>
                      </div>
                    )}

                    <div className="border-t pt-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="text-sm font-semibold">Audit Trail</h4>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => exportToPDF(history)}
                        >
                          <Download className="h-3 w-3 mr-1" />
                          Export PDF
                        </Button>
                      </div>

                      <div className="space-y-2">
                        {history.audit_trail.map((entry, index) => (
                          <div key={index} className="flex items-start gap-3 text-sm">
                            <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                            <div className="flex-1">
                              <p className="font-medium">{entry.step}</p>
                              <p className="text-gray-600">
                                {entry.action} by {entry.user}
                              </p>
                              <p className="text-xs text-gray-500">{formatDate(entry.timestamp)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredHistories.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-gray-500">
            No workflow history found matching your filters.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
