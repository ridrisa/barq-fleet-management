import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsAPI, emailTemplatesAPI } from '@/lib/adminAPI'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'

interface Setting {
  key: string
  value: any
  description: string
  category: string
}

interface EmailTemplate {
  id: number
  name: string
  subject: string
  body: string
  variables: string[]
  created_at: string
}

export default function Integrations() {
  const [activeTab, setActiveTab] = useState<'settings' | 'email-templates'>('settings')

  const queryClient = useQueryClient()

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsAPI.getAll(),
  })

  const { data: emailTemplates } = useQuery({
    queryKey: ['email-templates'],
    queryFn: () => emailTemplatesAPI.getAll(),
  })

  const updateSettingMutation = useMutation({
    mutationFn: ({ key, value }: { key: string; value: any }) =>
      settingsAPI.update(key, value),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      alert('Setting updated successfully')
    },
    onError: () => {
      alert('Failed to update setting')
    },
  })

  const sendTestEmailMutation = useMutation({
    mutationFn: ({ templateId, email }: { templateId: number; email: string }) =>
      emailTemplatesAPI.sendTest(templateId, email),
    onSuccess: () => {
      alert('Test email sent successfully')
    },
    onError: () => {
      alert('Failed to send test email')
    },
  })

  const groupedSettings: { [category: string]: Setting[] } = {}
  settings?.forEach((setting: Setting) => {
    if (!groupedSettings[setting.category]) {
      groupedSettings[setting.category] = []
    }
    groupedSettings[setting.category].push(setting)
  })

  const handleSendTest = (templateId: number) => {
    const email = prompt('Enter email address to send test:')
    if (email) {
      sendTestEmailMutation.mutate({ templateId, email })
    }
  }

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">System Settings & Integrations</h1>
          <p className="mt-2 text-sm text-gray-700">
            Configure system settings, email templates, and third-party integrations.
          </p>
        </div>
      </div>

      <div className="mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('settings')}
              className={`${
                activeTab === 'settings'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              System Settings
            </button>
            <button
              onClick={() => setActiveTab('email-templates')}
              className={`${
                activeTab === 'email-templates'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Email Templates
            </button>
          </nav>
        </div>
      </div>

      {activeTab === 'settings' && (
        <div className="mt-6 space-y-6">
          {Object.entries(groupedSettings).map(([category, categorySettings]) => (
            <Card key={category}>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 capitalize">
                  {category}
                </h3>
                <div className="space-y-4">
                  {categorySettings.map((setting: Setting) => (
                    <div key={setting.key} className="flex items-center justify-between">
                      <div className="flex-1">
                        <label className="text-sm font-medium text-gray-700">
                          {setting.key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </label>
                        <p className="text-xs text-gray-500 mt-1">{setting.description}</p>
                      </div>
                      <div className="ml-4 w-64">
                        {typeof setting.value === 'boolean' ? (
                          <select
                            value={setting.value.toString()}
                            onChange={(e) =>
                              updateSettingMutation.mutate({
                                key: setting.key,
                                value: e.target.value === 'true',
                              })
                            }
                            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                          >
                            <option value="true">Enabled</option>
                            <option value="false">Disabled</option>
                          </select>
                        ) : (
                          <Input
                            type="text"
                            value={setting.value}
                            onChange={(e) =>
                              updateSettingMutation.mutate({
                                key: setting.key,
                                value: e.target.value,
                              })
                            }
                          />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {activeTab === 'email-templates' && (
        <div className="mt-6">
          <div className="flex justify-end mb-4">
            <Button
              onClick={() => {
                alert('Template creation coming soon')
              }}
              className="bg-primary-600 text-white hover:bg-primary-500"
            >
              Create Template
            </Button>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {emailTemplates?.map((template: EmailTemplate) => (
              <Card key={template.id}>
                <CardContent className="pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {template.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">Subject: {template.subject}</p>
                  <div className="mb-4">
                    <p className="text-xs font-medium text-gray-700 mb-1">Available Variables:</p>
                    <div className="flex flex-wrap gap-1">
                      {template.variables.map((variable) => (
                        <Badge key={variable} variant="info">
                          {`{{${variable}}}`}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      onClick={() => handleSendTest(template.id)}
                      variant="outline"
                      size="sm"
                      className="flex-1"
                    >
                      Send Test
                    </Button>
                    <Button
                      onClick={() => {
                        alert('Template editing coming soon')
                      }}
                      variant="outline"
                      size="sm"
                      className="flex-1"
                    >
                      Edit
                    </Button>
                  </div>
                  <p className="text-xs text-gray-400 mt-4">
                    Created: {new Date(template.created_at).toLocaleDateString()}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Information Cards */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Integration Status</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Google OAuth</span>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Email Service</span>
                <Badge variant="success">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">SMS Gateway</span>
                <Badge variant="warning">Pending</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">Security Settings</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Two-Factor Auth</span>
                <Badge variant="success">Enabled</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Session Timeout</span>
                <span className="text-sm text-gray-900">15 minutes</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Password Policy</span>
                <Badge variant="success">Strong</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
