import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Save, Settings as SettingsIcon } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Settings() {
  const [settings, setSettings] = useState({
    defaultSLADays: '3',
    autoEscalationHours: '24',
    requireComments: true,
    allowParallelApprovals: false,
    defaultApproverRole: 'supervisor',
    timeoutAction: 'escalate',
    notifyOnSubmission: true,
    notifyOnApproval: true,
    notifyOnRejection: true,
    reminderFrequency: '24'
  })

  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Settings saved successfully')
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setSettings({
      defaultSLADays: '3',
      autoEscalationHours: '24',
      requireComments: true,
      allowParallelApprovals: false,
      defaultApproverRole: 'supervisor',
      timeoutAction: 'escalate',
      notifyOnSubmission: true,
      notifyOnApproval: true,
      notifyOnRejection: true,
      reminderFrequency: '24'
    })
    toast.success('Settings reset to defaults')
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow Settings</h1>
        <div className="flex gap-3">
          <Button variant="ghost" onClick={handleReset}>
            Reset to Defaults
          </Button>
          <Button onClick={handleSave} isLoading={saving}>
            <Save className="h-4 w-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5 text-gray-600" />
            <CardTitle>General Workflow Settings</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default SLA (Days)
              </label>
              <Input
                type="number"
                value={settings.defaultSLADays}
                onChange={(e) => setSettings({ ...settings, defaultSLADays: e.target.value })}
                min="1"
                max="30"
              />
              <p className="text-xs text-gray-500 mt-1">
                Default time limit for workflow completion
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Auto-Escalation (Hours)
              </label>
              <Input
                type="number"
                value={settings.autoEscalationHours}
                onChange={(e) => setSettings({ ...settings, autoEscalationHours: e.target.value })}
                min="1"
                max="72"
              />
              <p className="text-xs text-gray-500 mt-1">
                Time before escalating to next level
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Approver Role
              </label>
              <Select
                value={settings.defaultApproverRole}
                onChange={(e) => setSettings({ ...settings, defaultApproverRole: e.target.value })}
              >
                <option value="supervisor">Supervisor</option>
                <option value="manager">Manager</option>
                <option value="hr">HR</option>
                <option value="admin">Admin</option>
              </Select>
              <p className="text-xs text-gray-500 mt-1">
                Default role for first approver
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeout Action
              </label>
              <Select
                value={settings.timeoutAction}
                onChange={(e) => setSettings({ ...settings, timeoutAction: e.target.value })}
              >
                <option value="escalate">Escalate to Next Level</option>
                <option value="auto-reject">Auto Reject</option>
                <option value="notify-only">Notify Only</option>
              </Select>
              <p className="text-xs text-gray-500 mt-1">
                Action when SLA is exceeded
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reminder Frequency (Hours)
              </label>
              <Input
                type="number"
                value={settings.reminderFrequency}
                onChange={(e) => setSettings({ ...settings, reminderFrequency: e.target.value })}
                min="1"
                max="72"
              />
              <p className="text-xs text-gray-500 mt-1">
                How often to send pending approval reminders
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Approval Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Require Comments</p>
              <p className="text-sm text-gray-600">
                Force approvers to add comments when approving/rejecting
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.requireComments}
                onChange={(e) => setSettings({ ...settings, requireComments: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Allow Parallel Approvals</p>
              <p className="text-sm text-gray-600">
                Enable multiple approvers at the same level to approve simultaneously
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.allowParallelApprovals}
                onChange={(e) => setSettings({ ...settings, allowParallelApprovals: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Notification Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Notify on Submission</p>
              <p className="text-sm text-gray-600">
                Send notifications when a new workflow is submitted
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifyOnSubmission}
                onChange={(e) => setSettings({ ...settings, notifyOnSubmission: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Notify on Approval</p>
              <p className="text-sm text-gray-600">
                Send notifications when a workflow is approved
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifyOnApproval}
                onChange={(e) => setSettings({ ...settings, notifyOnApproval: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Notify on Rejection</p>
              <p className="text-sm text-gray-600">
                Send notifications when a workflow is rejected
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.notifyOnRejection}
                onChange={(e) => setSettings({ ...settings, notifyOnRejection: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
