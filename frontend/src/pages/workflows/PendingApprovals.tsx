import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

interface PendingApproval {
  id: number
  workflow_name: string
  entity_type: string
  entity_id: number
  requested_by: string
  request_date: string
  current_state: string
  sla_deadline?: string
  priority: 'low' | 'medium' | 'high'
  details: string
}

export default function PendingApprovals() {
  const [approvals, setApprovals] = useState<PendingApproval[]>([
    {
      id: 1,
      workflow_name: 'Leave Request',
      entity_type: 'Leave',
      entity_id: 123,
      requested_by: 'John Doe',
      request_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      current_state: 'Supervisor Review',
      sla_deadline: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
      priority: 'high',
      details: '3 days annual leave from Dec 20-22'
    },
    {
      id: 2,
      workflow_name: 'Vehicle Assignment',
      entity_type: 'Assignment',
      entity_id: 456,
      requested_by: 'Jane Smith',
      request_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      current_state: 'Manager Approval',
      priority: 'medium',
      details: 'Assign courier to vehicle #ABC-123'
    }
  ])
  const [selectedApproval, setSelectedApproval] = useState<PendingApproval | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null)
  const [comment, setComment] = useState('')
  const [processing, setProcessing] = useState(false)

  const handleOpenModal = (approval: PendingApproval, action: 'approve' | 'reject') => {
    setSelectedApproval(approval)
    setActionType(action)
    setIsModalOpen(true)
    setComment('')
  }

  const handleSubmitAction = async () => {
    if (!selectedApproval || !actionType) return

    setProcessing(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))

      setApprovals(approvals.filter(a => a.id !== selectedApproval.id))

      toast.success(
        actionType === 'approve'
          ? 'Request approved successfully'
          : 'Request rejected'
      )

      setIsModalOpen(false)
      setComment('')
    } catch (error) {
      toast.error('Failed to process request')
    } finally {
      setProcessing(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const isOverdue = (deadline?: string) => {
    if (!deadline) return false
    return new Date(deadline) < new Date()
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">My Pending Approvals</h1>
        <Badge className="bg-orange-100 text-orange-800 text-lg px-4 py-2">
          {approvals.length} Pending
        </Badge>
      </div>

      {approvals.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-gray-500">
            <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
            <p className="text-lg font-medium text-gray-700 mb-1">All caught up!</p>
            <p>You have no pending approvals at the moment.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {approvals.map((approval) => (
            <Card key={approval.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{approval.workflow_name}</h3>
                      <Badge className={getPriorityColor(approval.priority)}>
                        {approval.priority.toUpperCase()}
                      </Badge>
                      {approval.sla_deadline && isOverdue(approval.sla_deadline) && (
                        <Badge className="bg-red-100 text-red-800">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          OVERDUE
                        </Badge>
                      )}
                    </div>

                    <p className="text-sm text-gray-600 mb-3">
                      {approval.entity_type} #{approval.entity_id}
                    </p>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4 text-sm">
                      <div>
                        <span className="text-gray-600">Requested By:</span>
                        <p className="font-medium">{approval.requested_by}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Request Date:</span>
                        <p className="font-medium">{formatDate(approval.request_date)}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Current State:</span>
                        <p className="font-medium">{approval.current_state}</p>
                      </div>
                    </div>

                    <div className="p-3 bg-gray-50 rounded-lg mb-4">
                      <p className="text-sm font-semibold text-gray-700 mb-1">Details:</p>
                      <p className="text-sm text-gray-600">{approval.details}</p>
                    </div>

                    {approval.sla_deadline && (
                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="h-4 w-4 text-gray-500" />
                        <span className="text-gray-600">SLA Deadline:</span>
                        <span className={`font-medium ${isOverdue(approval.sla_deadline) ? 'text-red-600' : 'text-gray-900'}`}>
                          {formatDate(approval.sla_deadline)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex gap-3 pt-4 border-t">
                  <Button
                    variant="success"
                    onClick={() => handleOpenModal(approval, 'approve')}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Approve
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => handleOpenModal(approval, 'reject')}
                  >
                    <XCircle className="h-4 w-4 mr-2" />
                    Reject
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={actionType === 'approve' ? 'Approve Request' : 'Reject Request'}
        size="md"
      >
        {selectedApproval && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="font-semibold mb-2">{selectedApproval.workflow_name}</p>
              <p className="text-sm text-gray-600">{selectedApproval.details}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Comment {actionType === 'reject' ? '(Required)' : '(Optional)'}
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder={
                  actionType === 'approve'
                    ? 'Add a comment (optional)'
                    : 'Please provide a reason for rejection'
                }
                rows={4}
                required={actionType === 'reject'}
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button
                variant="ghost"
                onClick={() => setIsModalOpen(false)}
                disabled={processing}
              >
                Cancel
              </Button>
              <Button
                variant={actionType === 'approve' ? 'success' : 'danger'}
                onClick={handleSubmitAction}
                isLoading={processing}
                disabled={processing || (actionType === 'reject' && !comment.trim())}
              >
                {actionType === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
