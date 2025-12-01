import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Play, Pause, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'

interface AutomationRule {
  id: number
  rule_name: string
  condition: string
  action: string
  action_type: string
  is_active: boolean
  execution_count: number
  last_executed: string | null
  created_at: string
}

export default function Automations() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<AutomationRule | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [actionFilter, setActionFilter] = useState('')

  // Mock data
  const [rules, setRules] = useState<AutomationRule[]>([
    {
      id: 1,
      rule_name: 'Auto-assign Vehicles',
      condition: 'courier.status == "active" AND vehicle.status == "available"',
      action: 'Assign nearest available vehicle to courier',
      action_type: 'assignment',
      is_active: true,
      execution_count: 342,
      last_executed: '2024-01-07 16:30:00',
      created_at: '2024-01-01',
    },
    {
      id: 2,
      rule_name: 'Auto-approve Short Leave',
      condition: 'leave.days <= 2 AND courier.leave_balance >= leave.days',
      action: 'Automatically approve leave request',
      action_type: 'approval',
      is_active: true,
      execution_count: 156,
      last_executed: '2024-01-07 14:15:00',
      created_at: '2024-01-01',
    },
    {
      id: 3,
      rule_name: 'Schedule Maintenance Alert',
      condition: 'vehicle.mileage >= vehicle.next_maintenance_mileage - 500',
      action: 'Send maintenance reminder notification',
      action_type: 'notification',
      is_active: true,
      execution_count: 45,
      last_executed: '2024-01-07 09:00:00',
      created_at: '2024-01-02',
    },
    {
      id: 4,
      rule_name: 'Auto-calculate Bonus',
      condition: 'courier.deliveries_this_month >= 100',
      action: 'Calculate and add performance bonus',
      action_type: 'calculation',
      is_active: true,
      execution_count: 28,
      last_executed: '2024-01-06 23:59:00',
      created_at: '2024-01-01',
    },
    {
      id: 5,
      rule_name: 'Escalate Pending Tasks',
      condition: 'task.status == "pending" AND task.created_at < NOW() - INTERVAL 3 DAYS',
      action: 'Escalate to manager and send notification',
      action_type: 'escalation',
      is_active: false,
      execution_count: 12,
      last_executed: '2024-01-05 10:00:00',
      created_at: '2024-01-03',
    },
    {
      id: 6,
      rule_name: 'Auto-assign Route',
      condition: 'delivery.priority == "high" AND delivery.area IN courier.preferred_areas',
      action: 'Assign delivery to optimal courier',
      action_type: 'assignment',
      is_active: true,
      execution_count: 892,
      last_executed: '2024-01-07 17:00:00',
      created_at: '2024-01-01',
    },
  ])

  const actionTypes = [
    'assignment',
    'approval',
    'notification',
    'calculation',
    'escalation',
    'scheduling',
  ]

  const handleOpenCreateModal = () => {
    setEditingRule(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (rule: AutomationRule) => {
    setEditingRule(rule)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingRule(null)
  }

  const handleToggleActive = (id: number) => {
    setRules(rules.map(r =>
      r.id === id ? { ...r, is_active: !r.is_active } : r
    ))
  }

  const handleDelete = (id: number) => {
    if (window.confirm('Are you sure you want to delete this automation rule?')) {
      setRules(rules.filter(r => r.id !== id))
    }
  }

  // Filter rules
  const filteredRules = rules.filter(rule => {
    const matchesSearch = rule.rule_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rule.action.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesAction = !actionFilter || rule.action_type === actionFilter
    return matchesSearch && matchesAction
  })

  const activeRules = rules.filter(r => r.is_active).length
  const executedToday = rules.reduce((sum, r) => {
    if (r.last_executed && r.last_executed.startsWith('2024-01-07')) {
      return sum + r.execution_count
    }
    return sum
  }, 0)

  const columns = [
    {
      key: 'rule_name',
      header: 'Rule Name',
      sortable: true,
      render: (row: AutomationRule) => (
        <div className="flex items-start gap-2">
          <Zap className="h-4 w-4 text-yellow-600 mt-1 flex-shrink-0" />
          <div>
            <span className="font-medium">{row.rule_name}</span>
            <p className="text-xs text-gray-500 mt-1">{row.action}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'condition',
      header: 'Condition',
      render: (row: AutomationRule) => (
        <code className="text-xs bg-gray-100 px-2 py-1 rounded block max-w-xs overflow-hidden text-ellipsis">
          {row.condition}
        </code>
      ),
    },
    {
      key: 'action_type',
      header: 'Type',
      sortable: true,
      render: (row: AutomationRule) => {
        const colors: Record<string, string> = {
          assignment: 'blue',
          approval: 'green',
          notification: 'purple',
          calculation: 'orange',
          escalation: 'red',
          scheduling: 'indigo',
        }
        return (
          <Badge variant={colors[row.action_type] as any || 'default'}>
            {row.action_type}
          </Badge>
        )
      },
    },
    {
      key: 'execution_count',
      header: 'Executions',
      sortable: true,
      render: (row: AutomationRule) => (
        <div className="text-center">
          <p className="font-semibold">{row.execution_count}</p>
          <p className="text-xs text-gray-500">times</p>
        </div>
      ),
    },
    {
      key: 'last_executed',
      header: 'Last Executed',
      sortable: true,
      render: (row: AutomationRule) => (
        <span className="text-sm">
          {row.last_executed ? (
            <div>
              <p>{row.last_executed.split(' ')[0]}</p>
              <p className="text-xs text-gray-500">{row.last_executed.split(' ')[1]}</p>
            </div>
          ) : (
            'Never'
          )}
        </span>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (row: AutomationRule) => (
        <Badge variant={row.is_active ? 'success' : 'default'}>
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: AutomationRule) => (
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
        <h1 className="text-2xl font-bold">Automation Rules</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Rule
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {rules.length}
              </p>
              <p className="text-sm text-gray-600">Total Rules</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {activeRules}
              </p>
              <p className="text-sm text-gray-600">Active Rules</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {executedToday}
              </p>
              <p className="text-sm text-gray-600">Executed Today</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Rules Table */}
      <Card>
        <CardHeader>
          <CardTitle>Automation Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search rules by name or action..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <Select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              options={[
                { value: '', label: 'All Types' },
                ...actionTypes.map(type => ({
                  value: type,
                  label: type.charAt(0).toUpperCase() + type.slice(1),
                })),
              ]}
            />
          </div>
          <Table data={filteredRules} columns={columns} />
        </CardContent>
      </Card>

      {/* Rule Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingRule ? 'Edit Automation Rule' : 'Add New Automation Rule'}
        size="lg"
      >
        <AutomationRuleForm
          rule={editingRule}
          onClose={handleCloseModal}
          actionTypes={actionTypes}
        />
      </Modal>
    </div>
  )
}

// Simple form component
function AutomationRuleForm({
  rule,
  onClose,
  actionTypes
}: {
  rule: AutomationRule | null
  onClose: () => void
  actionTypes: string[]
}) {
  const [formData, setFormData] = useState({
    rule_name: rule?.rule_name || '',
    condition: rule?.condition || '',
    action: rule?.action || '',
    action_type: rule?.action_type || '',
    is_active: rule?.is_active ?? true,
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
          Rule Name
        </label>
        <Input
          value={formData.rule_name}
          onChange={(e) => setFormData({ ...formData, rule_name: e.target.value })}
          placeholder="Enter rule name"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Condition
        </label>
        <Input
          value={formData.condition}
          onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
          placeholder="e.g., leave.days <= 2 AND courier.leave_balance >= leave.days"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          Define when this rule should trigger
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Action Type
        </label>
        <Select
          value={formData.action_type}
          onChange={(e) => setFormData({ ...formData, action_type: e.target.value })}
          options={[
            { value: '', label: 'Select action type' },
            ...actionTypes.map(type => ({
              value: type,
              label: type.charAt(0).toUpperCase() + type.slice(1),
            })),
          ]}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Action
        </label>
        <Input
          value={formData.action}
          onChange={(e) => setFormData({ ...formData, action: e.target.value })}
          placeholder="Describe what action to take"
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          What should happen when the condition is met
        </p>
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
          {rule ? 'Update' : 'Create'} Rule
        </Button>
      </div>
    </form>
  )
}
