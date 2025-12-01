import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { settingsAPI } from '@/lib/api'
import { Save, Bell, Mail, MessageSquare, Smartphone } from 'lucide-react'
import toast from 'react-hot-toast'

interface NotificationPreference {
  event_type: string
  email: boolean
  sms: boolean
  push: boolean
  whatsapp: boolean
}

export default function NotificationSettings() {
  const queryClient = useQueryClient()

  // Fetch notification settings
  const { data: settings, isLoading } = useQuery({
    queryKey: ['notification-settings'],
    queryFn: settingsAPI.getNotifications,
  })

  const [preferences, setPreferences] = useState<NotificationPreference[]>(
    settings?.preferences || []
  )

  // Update when settings load
  useState(() => {
    if (settings?.preferences) {
      setPreferences(settings.preferences)
    }
  })

  // Update settings mutation
  const updateMutation = useMutation({
    mutationFn: settingsAPI.updateNotifications,
    onSuccess: () => {
      toast.success('Notification settings updated successfully')
      queryClient.invalidateQueries({ queryKey: ['notification-settings'] })
    },
    onError: () => {
      toast.error('Failed to update notification settings')
    },
  })

  const handleToggle = (eventType: string, channel: keyof Omit<NotificationPreference, 'event_type'>) => {
    setPreferences((prev) =>
      prev.map((pref) =>
        pref.event_type === eventType
          ? { ...pref, [channel]: !pref[channel] }
          : pref
      )
    )
  }

  const handleSubmit = () => {
    updateMutation.mutate({ preferences })
  }

  const notificationTypes = [
    {
      event_type: 'delivery_assigned',
      title: 'Delivery Assigned',
      description: 'When a new delivery is assigned to a courier',
    },
    {
      event_type: 'delivery_completed',
      title: 'Delivery Completed',
      description: 'When a delivery is marked as completed',
    },
    {
      event_type: 'vehicle_maintenance',
      title: 'Vehicle Maintenance Due',
      description: 'Upcoming or overdue vehicle maintenance',
    },
    {
      event_type: 'leave_request',
      title: 'Leave Request',
      description: 'When an employee submits a leave request',
    },
    {
      event_type: 'leave_approved',
      title: 'Leave Approved/Rejected',
      description: 'When a leave request is approved or rejected',
    },
    {
      event_type: 'cod_collection',
      title: 'COD Collection',
      description: 'Cash on delivery collection updates',
    },
    {
      event_type: 'incident_reported',
      title: 'Incident Reported',
      description: 'When a new incident is reported',
    },
    {
      event_type: 'attendance_anomaly',
      title: 'Attendance Anomaly',
      description: 'Late check-ins, missed check-outs, or absences',
    },
    {
      event_type: 'system_updates',
      title: 'System Updates',
      description: 'Important system announcements and updates',
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  // Initialize preferences if empty
  const currentPreferences =
    preferences.length > 0
      ? preferences
      : notificationTypes.map((type) => ({
          event_type: type.event_type,
          email: true,
          sms: false,
          push: true,
          whatsapp: false,
        }))

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">Notification Settings</h1>
        <p className="text-gray-600">
          Manage how you receive notifications for different events
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold">Event Type</th>
                  <th className="text-center py-3 px-4 font-semibold w-24">
                    <div className="flex flex-col items-center">
                      <Mail className="w-5 h-5 mb-1" />
                      <span className="text-xs">Email</span>
                    </div>
                  </th>
                  <th className="text-center py-3 px-4 font-semibold w-24">
                    <div className="flex flex-col items-center">
                      <MessageSquare className="w-5 h-5 mb-1" />
                      <span className="text-xs">SMS</span>
                    </div>
                  </th>
                  <th className="text-center py-3 px-4 font-semibold w-24">
                    <div className="flex flex-col items-center">
                      <Bell className="w-5 h-5 mb-1" />
                      <span className="text-xs">Push</span>
                    </div>
                  </th>
                  <th className="text-center py-3 px-4 font-semibold w-24">
                    <div className="flex flex-col items-center">
                      <Smartphone className="w-5 h-5 mb-1" />
                      <span className="text-xs">WhatsApp</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {notificationTypes.map((type) => {
                  const pref = currentPreferences.find(
                    (p) => p.event_type === type.event_type
                  ) || {
                    event_type: type.event_type,
                    email: true,
                    sms: false,
                    push: true,
                    whatsapp: false,
                  }

                  return (
                    <tr key={type.event_type} className="border-b hover:bg-gray-50">
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium">{type.title}</div>
                          <div className="text-sm text-gray-500">{type.description}</div>
                        </div>
                      </td>
                      <td className="text-center py-4 px-4">
                        <label className="inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={pref.email}
                            onChange={() => handleToggle(type.event_type, 'email')}
                            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </label>
                      </td>
                      <td className="text-center py-4 px-4">
                        <label className="inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={pref.sms}
                            onChange={() => handleToggle(type.event_type, 'sms')}
                            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </label>
                      </td>
                      <td className="text-center py-4 px-4">
                        <label className="inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={pref.push}
                            onChange={() => handleToggle(type.event_type, 'push')}
                            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </label>
                      </td>
                      <td className="text-center py-4 px-4">
                        <label className="inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={pref.whatsapp}
                            onChange={() => handleToggle(type.event_type, 'whatsapp')}
                            className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </label>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Additional Options */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <h3 className="font-semibold mb-3">Additional Options</h3>

          <label className="flex items-center justify-between p-3 border rounded-md hover:bg-gray-50 cursor-pointer">
            <div>
              <div className="font-medium">Email Digest</div>
              <div className="text-sm text-gray-500">Receive a daily summary of all notifications</div>
            </div>
            <input
              type="checkbox"
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>

          <label className="flex items-center justify-between p-3 border rounded-md hover:bg-gray-50 cursor-pointer">
            <div>
              <div className="font-medium">Do Not Disturb</div>
              <div className="text-sm text-gray-500">Silence notifications from 10 PM to 7 AM</div>
            </div>
            <input
              type="checkbox"
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>

          <label className="flex items-center justify-between p-3 border rounded-md hover:bg-gray-50 cursor-pointer">
            <div>
              <div className="font-medium">Marketing Notifications</div>
              <div className="text-sm text-gray-500">Receive updates about new features and promotions</div>
            </div>
            <input
              type="checkbox"
              className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <Button type="button" variant="outline">
          Reset to Defaults
        </Button>
        <Button onClick={handleSubmit} disabled={updateMutation.isPending}>
          <Save className="w-4 h-4 mr-2" />
          {updateMutation.isPending ? 'Saving...' : 'Save Notification Settings'}
        </Button>
      </div>
    </div>
  )
}
