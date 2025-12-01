import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { ticketsAPI } from '@/lib/api'
import { ArrowLeft, Send, Paperclip } from 'lucide-react'
import toast from 'react-hot-toast'

type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed'
type TicketPriority = 'low' | 'medium' | 'high' | 'urgent'

interface Comment {
  id: number
  author: string
  content: string
  created_at: string
}

export default function TicketDetails() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [comment, setComment] = useState('')

  // Fetch ticket details
  const { data: ticket, isLoading } = useQuery({
    queryKey: ['ticket', id],
    queryFn: () => ticketsAPI.getById(Number(id)),
    enabled: !!id,
  })

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: (status: TicketStatus) => ticketsAPI.updateStatus(Number(id), status),
    onSuccess: () => {
      toast.success('Status updated successfully')
      queryClient.invalidateQueries({ queryKey: ['ticket', id] })
    },
    onError: () => {
      toast.error('Failed to update status')
    },
  })

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: (comment: string) => ticketsAPI.addComment(Number(id), comment),
    onSuccess: () => {
      toast.success('Comment added successfully')
      queryClient.invalidateQueries({ queryKey: ['ticket', id] })
      setComment('')
    },
    onError: () => {
      toast.error('Failed to add comment')
    },
  })

  const handleStatusChange = (newStatus: string) => {
    const status = newStatus as TicketStatus
    updateStatusMutation.mutate(status)
  }

  const handleAddComment = () => {
    if (!comment.trim()) {
      toast.error('Please enter a comment')
      return
    }
    addCommentMutation.mutate(comment)
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

  if (!ticket) {
    return (
      <div className="text-center">
        <p className="text-red-600">Ticket not found</p>
        <Button onClick={() => navigate('/support/tickets')} className="mt-4">
          Back to Tickets
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={() => navigate('/support/tickets')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Ticket #{ticket.id}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Ticket Details */}
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div>
                <h2 className="text-xl font-semibold mb-2">{ticket.title}</h2>
                <div className="flex gap-2 mb-4">
                  {getStatusBadge(ticket.status)}
                  {getPriorityBadge(ticket.priority)}
                  <Badge>{ticket.category}</Badge>
                </div>
                <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>
              </div>

              <div className="border-t pt-4">
                <div className="text-sm text-gray-600">
                  <p>
                    Created by <span className="font-medium">{ticket.created_by}</span> on{' '}
                    {new Date(ticket.created_at).toLocaleString()}
                  </p>
                  {ticket.assigned_to && (
                    <p>
                      Assigned to <span className="font-medium">{ticket.assigned_to}</span>
                    </p>
                  )}
                  <p>Last updated: {new Date(ticket.updated_at).toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Comments */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Conversation</h3>

              {/* Comments List */}
              <div className="space-y-4 mb-6">
                {ticket.comments && ticket.comments.length > 0 ? (
                  ticket.comments.map((comment: Comment) => (
                    <div key={comment.id} className="border-l-2 border-blue-500 pl-4 py-2">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium">{comment.author}</span>
                        <span className="text-sm text-gray-500">
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-gray-700 whitespace-pre-wrap">{comment.content}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No comments yet</p>
                )}
              </div>

              {/* Add Comment */}
              <div className="border-t pt-4">
                <label className="block text-sm font-medium mb-2">Add Comment</label>
                <textarea
                  className="w-full border rounded-md p-3 min-h-[100px] mb-3"
                  placeholder="Write your comment here..."
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                />
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" size="sm">
                    <Paperclip className="w-4 h-4 mr-2" />
                    Attach File
                  </Button>
                  <Button
                    onClick={handleAddComment}
                    disabled={addCommentMutation.isPending || !comment.trim()}
                  >
                    <Send className="w-4 h-4 mr-2" />
                    {addCommentMutation.isPending ? 'Sending...' : 'Send Comment'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Update */}
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Status</label>
                <Select
                  value={ticket.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  options={[
                    { value: 'open', label: 'Open' },
                    { value: 'in_progress', label: 'In Progress' },
                    { value: 'resolved', label: 'Resolved' },
                    { value: 'closed', label: 'Closed' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Priority</label>
                <div className="py-2">{getPriorityBadge(ticket.priority)}</div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Category</label>
                <p className="text-gray-700">{ticket.category}</p>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardContent className="pt-6 space-y-2">
              <Button className="w-full" variant="outline">
                Assign to Agent
              </Button>
              <Button className="w-full" variant="outline">
                Change Priority
              </Button>
              <Button className="w-full" variant="outline">
                Close Ticket
              </Button>
            </CardContent>
          </Card>

          {/* Attachments */}
          <Card>
            <CardContent className="pt-6">
              <h4 className="font-medium mb-3">Attachments</h4>
              <p className="text-sm text-gray-500">No attachments</p>
              <Button className="w-full mt-3" variant="outline" size="sm">
                <Paperclip className="w-4 h-4 mr-2" />
                Upload Attachment
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
