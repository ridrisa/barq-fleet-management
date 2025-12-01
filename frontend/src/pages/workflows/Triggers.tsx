import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Play, Pause } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'

interface Trigger {
  id: number
  trigger_name: string
  event_type: string
  conditions: string
  workflow_id: string
  workflow_name: string
  is_active: boolean
  triggered_count: number
  last_triggered: string | null
}

export default function Triggers() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingTrigger, setEditingTrigger] = useState<Trigger | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [eventFilter, setEventFilter] = useState('')

  // Mock data
  const [triggers, setTriggers] = useState<Trigger[]>([
    {
      id: 1,
      trigger_name: 'New Courier Onboarding',
      event_type: 'courier_created',
      conditions: 'status == "pending"',
      workflow_id: 'wf_001',
      workflow_name: 'Courier Onboarding Process',
      is_active: true,
      triggered_count: 45,
      last_triggered: '2024-01-07 15:30:00',
    },
    {
      id: 2,
      trigger_name: 'Delivery Completion',
      event_type: 'delivery_completed',
      conditions: 'delivery_type == "cod"',
      workflow_id: 'wf_002',
      workflow_name: 'COD Reconciliation',
      is_active: true,
      triggered_count: 1250,
      last_triggered: '2024-01-07 16:45:00',
    },
    {
      id: 3,
      trigger_name: 'Leave Request Notification',
      event_type: 'leave_requested',
      conditions: 'days > 3',
      workflow_id: 'wf_003',
      workflow_name: 'Leave Approval Chain',
      is_active: true,
      triggered_count: 28,
      last_triggered: '2024-01-06 09:20:00',
    },
    {
      id: 4,
      trigger_name: 'Vehicle Maintenance Alert',
      event_type: 'vehicle_mileage_threshold',
      conditions: 'mileage >= 10000',
      workflow_id: 'wf_004',
      workflow_name: 'Maintenance Scheduling',
      is_active: false,
      triggered_count: 12,
      last_triggered: '2024-01-05 14:15:00',
    },
    {
      id: 5,
      trigger_name: 'Incident Escalation',
      event_type: 'incident_reported',
      conditions: 'severity == "high"',
      workflow_id: 'wf_005',
      workflow_name: 'Incident Management',
      is_active: true,
      triggered_count: 8,
      last_triggered: '2024-01-07 11:00:00',
    },
  ])

  const eventTypes = [
    'courier_created',
    'delivery_completed',
    'leave_requested',
    'vehicle_mileage_threshold',
    'incident_reported',
    'payment_received',
    'bonus_calculated',
    'contract_expiring',
  ]

  const handleOpenCreateModal = () => {
    setEditingTrigger(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (trigger: Trigger) => {
    setEditingTrigger(trigger)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingTrigger(null)
  }

  const handleToggleActive = (id: number) => {
    setTriggers(triggers.map(t =>
      t.id === id ? { ...t, is_active: !t.is_active } : t
    ))
  }

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this trigger?')) {
      setTriggers(triggers.filter(t => t.id !== id))
    }
  }

  // Filter triggers
  const filteredTriggers = triggers.filter(trigger => {
    const matchesSearch = trigger.trigger_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         trigger.event_type.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesEvent = !eventFilter || trigger.event_type === eventFilter
    return matchesSearch && matchesEvent
  })

  const activeTriggers = triggers.filter(t => t.is_active).length
  const triggeredToday = triggers.reduce((sum, t) => {
    if (t.last_triggered && t.last_triggered.startsWith('2024-01-07')) {
      return sum + 1
    }
    return sum
  }, 0)

  const columns = [
    {
      key: 'trigger_name',
      header: 'Trigger Name',
      sortable: true,
      render: (row: Trigger) => (
        <div>
          <span className="font-medium">{row.trigger_name}</span>
          <p className="text-xs text-gray-500 mt-1">{row.workflow_name}</p>
        </div>
      ),
    },
    {
      key: 'event_type',
      header: 'Event Type',
      sortable: true,
      render: (row: Trigger) => (
        <Badge variant="default">
          {row.event_type.replace(/_/g, ' ')}
        </Badge>
      ),
    },
    {
      key: 'conditions',
      header: 'Conditions',
      render: (row: Trigger) => (
        <code className="text-xs bg-gray-100 px-2 py-1 rounded">
          {row.conditions}
        </code>
      ),
    },
    {
      key: 'triggered_count',
      header: 'Triggered',
      sortable: true,
      render: (row: Trigger) => (
        <div className="text-center">
          <p className="font-semibold">{row.triggered_count}</p>
          <p className="text-xs text-gray-500">times</p>
        </div>
      ),
    },
    {
      key: 'last_triggered',
      header: 'Last Triggered',
      sortable: true,
      render: (row: Trigger) => (
        <span className="text-sm">
          {row.last_triggered || 'Never'}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (row: Trigger) => (
        <Badge variant={row.is_active ? 'success' : 'default'}>
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: Trigger) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleToggleActive(row.id)}
            title={row.is_active ? 'Deactivate' : 'Activate'}
          >
            {row.is_active ? (
              <Pause className="h-4 w-4 text-orange-600" />
            ) : (
              <Play className="h-4 w-4 text-green-600" />
            )}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
          >
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow Triggers</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Trigger
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {triggers.length}
              </p>
              <p className="text-sm text-gray-600">Total Triggers</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {activeTriggers}
              </p>
              <p className="text-sm text-gray-600">Active Triggers</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {triggeredToday}
              </p>
              <p className="text-sm text-gray-600">Triggered Today</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Triggers Table */}
      <Card>
        <CardHeader>
          <CardTitle>Triggers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search triggers by name or event type..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <Select
              value={eventFilter}
              onChange={(e) => setEventFilter(e.target.value)}
              options={[
                { value: '', label: 'All Event Types' },
                ...eventTypes.map(type => ({
                  value: type,
                  label: type.replace(/_/g, ' '),
                })),
              ]}
            />
          </div>
          <Table data={filteredTriggers} columns={columns} />
        </CardContent>
      </Card>

      {/* Trigger Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingTrigger ? 'Edit Trigger' : 'Add New Trigger'}
        size="lg"
      >
        <TriggerForm
          trigger={editingTrigger}
          onClose={handleCloseModal}
          eventTypes={eventTypes}
        />
      </Modal>
    </div>
  )
}

// Simple form component
function TriggerForm({
  trigger,
  onClose,
  eventTypes
}: {
  trigger: Trigger | null
  onClose: () => void
  eventTypes: string[]
}) {
  const [formData, setFormData] = useState({
    trigger_name: trigger?.trigger_name || '',
    event_type: trigger?.event_type || '',
    conditions: trigger?.conditions || '',
    workflow_id: trigger?.workflow_id || '',
    is_active: trigger?.is_active ?? true,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission
    console.log('Form data:', formData)
    onClose()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Trigger Name
        </label>
        <Input
          value={formData.trigger_name}
          onChange={(e) => setFormData({ ...formData, trigger_name: e.target.value })}
          placeholder="Enter trigger name"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Event Type
        </label>
        <Select
          value={formData.event_type}
          onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
          options={[
            { value: '', label: 'Select event type' },
            ...eventTypes.map(type => ({
              value: type,
              label: type.replace(/_/g, ' '),
            })),
          ]}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Conditions
        </label>
        <Input
          value={formData.conditions}
          onChange={(e) => setFormData({ ...formData, conditions: e.target.value })}
          placeholder="e.g., status == 'pending'"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Workflow ID
        </label>
        <Input
          value={formData.workflow_id}
          onChange={(e) => setFormData({ ...formData, workflow_id: e.target.value })}
          placeholder="Enter workflow ID"
          required
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          className="rounded border-gray-300"
        />
        <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
          Active
        </label>
      </div>

      <div className="flex justify-end gap-2 mt-6">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit">
          {trigger ? 'Update' : 'Create'} Trigger
        </Button>
      </div>
    </form>
  )
}
