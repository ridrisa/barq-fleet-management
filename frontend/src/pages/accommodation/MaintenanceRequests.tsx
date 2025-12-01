import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { FileUpload } from '@/components/ui/FileUpload'

interface MaintenanceRequest {
  id: number
  building_name: string
  room_number: string
  issue_type: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'open' | 'in_progress' | 'completed' | 'cancelled'
  reported_by: string
  reported_date: string
  assigned_to: string | null
  photos: string[]
}

export default function MaintenanceRequests() {
  const [requests, setRequests] = useState<MaintenanceRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [_editingRequest, _setEditingRequest] = useState<MaintenanceRequest | null>(null)
  const [photos, setPhotos] = useState<File[]>([])

  const [formData, setFormData] = useState({
    building_id: 0,
    room_number: '',
    issue_type: '',
    description: '',
    priority: 'medium' as MaintenanceRequest['priority'],
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      // Mock data
      const mockRequests: MaintenanceRequest[] = [
        {
          id: 1,
          building_name: 'Downtown Residence',
          room_number: '101',
          issue_type: 'Air Conditioning',
          description: 'AC not cooling properly, needs servicing',
          priority: 'high',
          status: 'in_progress',
          reported_by: 'Ahmed Ali',
          reported_date: '2024-03-01',
          assigned_to: 'Maintenance Team A',
          photos: ['/placeholder-ac.jpg'],
        },
        {
          id: 2,
          building_name: 'Marina Tower',
          room_number: '305',
          issue_type: 'Plumbing',
          description: 'Leaking faucet in bathroom',
          priority: 'medium',
          status: 'open',
          reported_by: 'Manager 1',
          reported_date: '2024-03-05',
          assigned_to: null,
          photos: [],
        },
        {
          id: 3,
          building_name: 'Downtown Residence',
          room_number: '201',
          issue_type: 'Electrical',
          description: 'Light fixtures not working in bedroom',
          priority: 'urgent',
          status: 'open',
          reported_by: 'Mohammed Hassan',
          reported_date: '2024-03-06',
          assigned_to: null,
          photos: ['/placeholder-light.jpg'],
        },
      ]
      setRequests(mockRequests)
    } catch (error) {
      console.error('Failed to fetch requests:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      console.log('Creating maintenance request:', formData, photos)
      // API call would go here
      fetchData()
      handleCloseModal()
    } catch (error) {
      console.error('Failed to create request:', error)
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    _setEditingRequest(null)
    setFormData({
      building_id: 0,
      room_number: '',
      issue_type: '',
      description: '',
      priority: 'medium',
    })
    setPhotos([])
  }

  const getPriorityColor = (priority: MaintenanceRequest['priority']) => {
    const colors = {
      low: 'secondary',
      medium: 'primary',
      high: 'warning',
      urgent: 'error',
    }
    return colors[priority] as 'secondary' | 'primary' | 'warning' | 'error'
  }

  const getStatusColor = (status: MaintenanceRequest['status']) => {
    const colors = {
      open: 'warning',
      in_progress: 'primary',
      completed: 'success',
      cancelled: 'error',
    }
    return colors[status] as 'warning' | 'primary' | 'success' | 'error'
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Maintenance Requests</h1>
        <Button onClick={() => setShowModal(true)}>New Request</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{requests.length}</div>
            <div className="text-sm text-gray-600">Total Requests</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-yellow-600">
              {requests.filter((r) => r.status === 'open').length}
            </div>
            <div className="text-sm text-gray-600">Open</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">
              {requests.filter((r) => r.status === 'in_progress').length}
            </div>
            <div className="text-sm text-gray-600">In Progress</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">
              {requests.filter((r) => r.priority === 'urgent').length}
            </div>
            <div className="text-sm text-gray-600">Urgent</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-4">
              {requests.map((request) => (
                <Card key={request.id} className="border-l-4 border-orange-500">
                  <CardContent className="pt-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">
                          {request.building_name} - Room {request.room_number}
                        </h3>
                        <p className="text-sm text-gray-600">{request.issue_type}</p>
                      </div>
                      <div className="flex gap-2">
                        <Badge variant={getPriorityColor(request.priority)}>
                          {request.priority}
                        </Badge>
                        <Badge variant={getStatusColor(request.status)}>
                          {request.status}
                        </Badge>
                      </div>
                    </div>

                    <p className="text-sm mb-3">{request.description}</p>

                    {request.photos.length > 0 && (
                      <div className="mb-3">
                        <p className="text-xs text-gray-500 mb-2">Photos:</p>
                        <div className="flex gap-2">
                          {request.photos.map((_photo, idx) => (
                            <div
                              key={idx}
                              className="w-20 h-20 bg-gray-200 rounded flex items-center justify-center"
                            >
                              <svg
                                className="w-8 h-8 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                                />
                              </svg>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex justify-between text-xs text-gray-500">
                      <span>
                        Reported by: {request.reported_by} on{' '}
                        {new Date(request.reported_date).toLocaleDateString()}
                      </span>
                      {request.assigned_to && (
                        <span>Assigned to: {request.assigned_to}</span>
                      )}
                    </div>

                    <div className="flex gap-2 mt-3">
                      <Button variant="outline" size="sm">
                        Update Status
                      </Button>
                      <Button variant="outline" size="sm">
                        Assign
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title="New Maintenance Request"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Building</label>
            <Select
              required
              value={formData.building_id}
              onChange={(e) =>
                setFormData({ ...formData, building_id: parseInt(e.target.value) })
              }
            >
              <option value="">Select Building</option>
              <option value="1">Downtown Residence</option>
              <option value="2">Marina Tower</option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Room Number</label>
            <Input
              required
              value={formData.room_number}
              onChange={(e) =>
                setFormData({ ...formData, room_number: e.target.value })
              }
              placeholder="101"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Issue Type</label>
            <Select
              required
              value={formData.issue_type}
              onChange={(e) =>
                setFormData({ ...formData, issue_type: e.target.value })
              }
            >
              <option value="">Select Type</option>
              <option value="Air Conditioning">Air Conditioning</option>
              <option value="Plumbing">Plumbing</option>
              <option value="Electrical">Electrical</option>
              <option value="Furniture">Furniture</option>
              <option value="Cleaning">Cleaning</option>
              <option value="Other">Other</option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              required
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows={3}
              placeholder="Describe the issue..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Priority</label>
            <Select
              value={formData.priority}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  priority: e.target.value as MaintenanceRequest['priority'],
                })
              }
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Upload Photos</label>
            <FileUpload
              accept={{ 'image/*': ['.png', '.jpg', '.jpeg'] }}
              maxFiles={5}
              maxSize={5 * 1024 * 1024}
              onFilesSelected={setPhotos}
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              Submit Request
            </Button>
            <Button type="button" variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
