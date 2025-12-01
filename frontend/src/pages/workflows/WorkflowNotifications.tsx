import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Bell, Mail, MessageSquare, Save } from 'lucide-react'
import toast from 'react-hot-toast'

interface NotificationPreference {
  event: string
  email: boolean
  sms: boolean
  inApp: boolean
}

export default function WorkflowNotifications() {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([
    { event: 'Workflow Submitted', email: true, sms: false, inApp: true },
    { event: 'Pending Approval', email: true, sms: true, inApp: true },
    { event: 'Workflow Approved', email: true, sms: false, inApp: true },
    { event: 'Workflow Rejected', email: true, sms: true, inApp: true },
    { event: 'SLA Deadline Approaching', email: true, sms: true, inApp: true },
    { event: 'SLA Deadline Exceeded', email: true, sms: true, inApp: true },
    { event: 'Workflow Escalated', email: true, sms: false, inApp: true },
    { event: 'Workflow Completed', email: false, sms: false, inApp: true }
  ])

  const [reminderSettings, setReminderSettings] = useState({
    enableReminders: true,
    reminderFrequency: '24',
    reminderTime: '09:00',
    stopAfterDays: '7'
  })

  const [saving, setSaving] = useState(false)

  const handleToggle = (index: number, channel: 'email' | 'sms' | 'inApp') => {
    const newPreferences = [...preferences]
    newPreferences[index][channel] = !newPreferences[index][channel]
    setPreferences(newPreferences)
  }

  const handleSave = async () => {
    setSaving(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Notification preferences saved successfully')
    } catch (error) {
      toast.error('Failed to save preferences')
    } finally {
      setSaving(false)
    }
  }

  const handleSelectAll = (channel: 'email' | 'sms' | 'inApp') => {
    const allEnabled = preferences.every(p => p[channel])
    setPreferences(preferences.map(p => ({ ...p, [channel]: !allEnabled })))
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow Notifications</h1>
        <Button onClick={handleSave} isLoading={saving}>
          <Save className="h-4 w-4 mr-2" />
          Save Preferences
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-gray-600" />
            <CardTitle>Notification Channels</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold">Event</th>
                  <th className="text-center py-3 px-4 font-semibold">
                    <div className="flex flex-col items-center gap-1">
                      <Mail className="h-4 w-4" />
                      <span>Email</span>
                      <button
                        onClick={() => handleSelectAll('email')}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Toggle All
                      </button>
                    </div>
                  </th>
                  <th className="text-center py-3 px-4 font-semibold">
                    <div className="flex flex-col items-center gap-1">
                      <MessageSquare className="h-4 w-4" />
                      <span>SMS</span>
                      <button
                        onClick={() => handleSelectAll('sms')}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Toggle All
                      </button>
                    </div>
                  </th>
                  <th className="text-center py-3 px-4 font-semibold">
                    <div className="flex flex-col items-center gap-1">
                      <Bell className="h-4 w-4" />
                      <span>In-App</span>
                      <button
                        onClick={() => handleSelectAll('inApp')}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Toggle All
                      </button>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {preferences.map((pref, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{pref.event}</td>
                    <td className="py-3 px-4 text-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={pref.email}
                          onChange={() => handleToggle(index, 'email')}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={pref.sms}
                          onChange={() => handleToggle(index, 'sms')}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={pref.inApp}
                          onChange={() => handleToggle(index, 'inApp')}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reminder Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium">Enable Reminders</p>
              <p className="text-sm text-gray-600">
                Send periodic reminders for pending approvals
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={reminderSettings.enableReminders}
                onChange={(e) => setReminderSettings({ ...reminderSettings, enableReminders: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          {reminderSettings.enableReminders && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reminder Frequency
                </label>
                <Select
                  value={reminderSettings.reminderFrequency}
                  onChange={(e) => setReminderSettings({ ...reminderSettings, reminderFrequency: e.target.value })}
                >
                  <option value="12">Every 12 hours</option>
                  <option value="24">Daily</option>
                  <option value="48">Every 2 days</option>
                  <option value="72">Every 3 days</option>
                </Select>
                <p className="text-xs text-gray-500 mt-1">
                  How often to send reminders
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reminder Time
                </label>
                <input
                  type="time"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={reminderSettings.reminderTime}
                  onChange={(e) => setReminderSettings({ ...reminderSettings, reminderTime: e.target.value })}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Preferred time for reminders
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stop After (Days)
                </label>
                <Select
                  value={reminderSettings.stopAfterDays}
                  onChange={(e) => setReminderSettings({ ...reminderSettings, stopAfterDays: e.target.value })}
                >
                  <option value="3">3 days</option>
                  <option value="7">7 days</option>
                  <option value="14">14 days</option>
                  <option value="30">30 days</option>
                  <option value="never">Never stop</option>
                </Select>
                <p className="text-xs text-gray-500 mt-1">
                  When to stop sending reminders
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Notification Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Mail className="h-5 w-5 text-blue-600" />
                <p className="font-semibold">Email</p>
              </div>
              <p className="text-2xl font-bold text-blue-600">
                {preferences.filter(p => p.email).length}
              </p>
              <p className="text-sm text-gray-600">events enabled</p>
            </div>

            <div className="p-4 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="h-5 w-5 text-green-600" />
                <p className="font-semibold">SMS</p>
              </div>
              <p className="text-2xl font-bold text-green-600">
                {preferences.filter(p => p.sms).length}
              </p>
              <p className="text-sm text-gray-600">events enabled</p>
            </div>

            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Bell className="h-5 w-5 text-purple-600" />
                <p className="font-semibold">In-App</p>
              </div>
              <p className="text-2xl font-bold text-purple-600">
                {preferences.filter(p => p.inApp).length}
              </p>
              <p className="text-sm text-gray-600">events enabled</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
