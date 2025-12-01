import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { Building2, Globe, Clock, DollarSign, Settings as SettingsIcon, Save, RotateCcw, CheckCircle, XCircle } from 'lucide-react'
import toast from 'react-hot-toast'

interface SystemSettingsData {
  id: number
  company_name: string
  company_logo_url: string | null
  company_address: string
  company_phone: string
  company_email: string
  timezone: string
  language: string
  currency: string
  date_format: string
  time_format: string
  business_hours_start: string
  business_hours_end: string
  module_fleet_enabled: boolean
  module_hr_finance_enabled: boolean
  module_accommodation_enabled: boolean
  module_workflows_enabled: boolean
  module_analytics_enabled: boolean
  integration_google_oauth: boolean
  integration_sms_provider: string
  integration_email_service: string
  updated_at: string
}

export default function SystemSettings() {
  const queryClient = useQueryClient()
  const [activeSection, setActiveSection] = useState<'company' | 'preferences' | 'business' | 'modules' | 'integrations'>('company')

  const [formData, setFormData] = useState<Partial<SystemSettingsData>>({
    company_name: '',
    company_logo_url: '',
    company_address: '',
    company_phone: '',
    company_email: '',
    timezone: 'Asia/Riyadh',
    language: 'en',
    currency: 'SAR',
    date_format: 'DD/MM/YYYY',
    time_format: '24h',
    business_hours_start: '09:00',
    business_hours_end: '18:00',
    module_fleet_enabled: true,
    module_hr_finance_enabled: true,
    module_accommodation_enabled: true,
    module_workflows_enabled: true,
    module_analytics_enabled: true,
    integration_google_oauth: false,
    integration_sms_provider: 'twilio',
    integration_email_service: 'smtp',
  })

  // Fetch system settings
  const { data: settings, isLoading } = useQuery({
    queryKey: ['system-settings'],
    queryFn: async () => {
      // Mock API call - in real app this would fetch from backend
      return {
        id: 1,
        company_name: 'BARQ Fleet Management',
        company_logo_url: null,
        company_address: 'Riyadh, Saudi Arabia',
        company_phone: '+966 50 123 4567',
        company_email: 'info@barqfleet.com',
        timezone: 'Asia/Riyadh',
        language: 'en',
        currency: 'SAR',
        date_format: 'DD/MM/YYYY',
        time_format: '24h',
        business_hours_start: '09:00',
        business_hours_end: '18:00',
        module_fleet_enabled: true,
        module_hr_finance_enabled: true,
        module_accommodation_enabled: true,
        module_workflows_enabled: true,
        module_analytics_enabled: true,
        integration_google_oauth: false,
        integration_sms_provider: 'twilio',
        integration_email_service: 'smtp',
        updated_at: new Date().toISOString(),
      } as SystemSettingsData
    },
  })

  // Update form when settings data loads
  useEffect(() => {
    if (settings) {
      setFormData(settings)
    }
  }, [settings])

  // Update settings mutation
  const updateSettingsMutation = useMutation({
    mutationFn: async (data: Partial<SystemSettingsData>) => {
      // Mock API call - in real app this would update backend
      return data
    },
    onSuccess: () => {
      toast.success('System settings updated successfully')
      queryClient.invalidateQueries({ queryKey: ['system-settings'] })
    },
    onError: () => {
      toast.error('Failed to update system settings')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateSettingsMutation.mutate(formData)
  }

  const handleReset = () => {
    if (settings) {
      setFormData(settings)
      toast.success('Settings reset to last saved values')
    }
  }

  const updateField = (field: keyof SystemSettingsData, value: any) => {
    setFormData({ ...formData, [field]: value })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  const sections = [
    { id: 'company' as const, label: 'Company Information', icon: Building2 },
    { id: 'preferences' as const, label: 'System Preferences', icon: Globe },
    { id: 'business' as const, label: 'Business Hours', icon: Clock },
    { id: 'modules' as const, label: 'Feature Modules', icon: SettingsIcon },
    { id: 'integrations' as const, label: 'Integrations', icon: DollarSign },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">System Settings</h1>
        <div className="flex gap-2">
          <Button onClick={handleReset} variant="outline">
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSubmit} disabled={updateSettingsMutation.isPending}>
            <Save className="w-4 h-4 mr-2" />
            {updateSettingsMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {/* Section Tabs */}
      <div className="flex gap-2 border-b overflow-x-auto">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
              activeSection === section.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <section.icon className="w-4 h-4" />
            {section.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Company Information */}
        {activeSection === 'company' && (
          <Card>
            <CardHeader>
              <CardTitle>
                <div className="flex items-center">
                  <Building2 className="h-5 w-5 mr-2" />
                  Company Information
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Company Name *</label>
                  <Input
                    value={formData.company_name}
                    onChange={(e) => updateField('company_name', e.target.value)}
                    placeholder="Enter company name"
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Company Logo URL</label>
                  <Input
                    value={formData.company_logo_url || ''}
                    onChange={(e) => updateField('company_logo_url', e.target.value)}
                    placeholder="https://example.com/logo.png"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium mb-2">Address *</label>
                  <Input
                    value={formData.company_address}
                    onChange={(e) => updateField('company_address', e.target.value)}
                    placeholder="Enter company address"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Phone *</label>
                  <Input
                    value={formData.company_phone}
                    onChange={(e) => updateField('company_phone', e.target.value)}
                    placeholder="+966 50 123 4567"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Email *</label>
                  <Input
                    type="email"
                    value={formData.company_email}
                    onChange={(e) => updateField('company_email', e.target.value)}
                    placeholder="info@company.com"
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* System Preferences */}
        {activeSection === 'preferences' && (
          <Card>
            <CardHeader>
              <CardTitle>
                <div className="flex items-center">
                  <Globe className="h-5 w-5 mr-2" />
                  System Preferences
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Timezone *</label>
                  <Select
                    value={formData.timezone}
                    onChange={(e) => updateField('timezone', e.target.value)}
                    options={[
                      { value: 'UTC', label: 'UTC' },
                      { value: 'Asia/Riyadh', label: 'Asia/Riyadh (GMT+3)' },
                      { value: 'Asia/Dubai', label: 'Asia/Dubai (GMT+4)' },
                      { value: 'Europe/London', label: 'Europe/London (GMT+0)' },
                      { value: 'America/New_York', label: 'America/New_York (GMT-5)' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Language *</label>
                  <Select
                    value={formData.language}
                    onChange={(e) => updateField('language', e.target.value)}
                    options={[
                      { value: 'en', label: 'English' },
                      { value: 'ar', label: 'Arabic (العربية)' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Currency *</label>
                  <Select
                    value={formData.currency}
                    onChange={(e) => updateField('currency', e.target.value)}
                    options={[
                      { value: 'SAR', label: 'SAR - Saudi Riyal' },
                      { value: 'SAR', label: 'SAR - Saudi Riyal' },
                      { value: 'USD', label: 'USD - US Dollar' },
                      { value: 'EUR', label: 'EUR - Euro' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Date Format *</label>
                  <Select
                    value={formData.date_format}
                    onChange={(e) => updateField('date_format', e.target.value)}
                    options={[
                      { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
                      { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
                      { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Time Format *</label>
                  <Select
                    value={formData.time_format}
                    onChange={(e) => updateField('time_format', e.target.value)}
                    options={[
                      { value: '24h', label: '24-hour (23:59)' },
                      { value: '12h', label: '12-hour (11:59 PM)' },
                    ]}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Business Hours */}
        {activeSection === 'business' && (
          <Card>
            <CardHeader>
              <CardTitle>
                <div className="flex items-center">
                  <Clock className="h-5 w-5 mr-2" />
                  Business Hours Configuration
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Start Time *</label>
                  <Input
                    type="time"
                    value={formData.business_hours_start}
                    onChange={(e) => updateField('business_hours_start', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">End Time *</label>
                  <Input
                    type="time"
                    value={formData.business_hours_end}
                    onChange={(e) => updateField('business_hours_end', e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-900">
                  Business hours are used to calculate delivery time estimates, SLA tracking, and working day calculations.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Feature Modules */}
        {activeSection === 'modules' && (
          <Card>
            <CardHeader>
              <CardTitle>
                <div className="flex items-center">
                  <SettingsIcon className="h-5 w-5 mr-2" />
                  Feature Modules (Enable/Disable)
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                {[
                  { key: 'module_fleet_enabled' as const, label: 'Fleet Management', description: 'Courier and vehicle management' },
                  { key: 'module_hr_finance_enabled' as const, label: 'HR & Finance', description: 'Payroll, expenses, and HR operations' },
                  { key: 'module_accommodation_enabled' as const, label: 'Accommodation', description: 'Housing and bed management' },
                  { key: 'module_workflows_enabled' as const, label: 'Workflows & Automation', description: 'Workflow builder and approval chains' },
                  { key: 'module_analytics_enabled' as const, label: 'Analytics & Reporting', description: 'Advanced analytics and custom reports' },
                ].map((module) => (
                  <label
                    key={module.key}
                    className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
                  >
                    <div>
                      <p className="font-medium">{module.label}</p>
                      <p className="text-sm text-gray-500">{module.description}</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={formData[module.key]}
                      onChange={(e) => updateField(module.key, e.target.checked)}
                      className="w-5 h-5 text-blue-600"
                    />
                  </label>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Integrations */}
        {activeSection === 'integrations' && (
          <Card>
            <CardHeader>
              <CardTitle>
                <div className="flex items-center">
                  <DollarSign className="h-5 w-5 mr-2" />
                  Integration Settings
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Google OAuth */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                      <span className="text-red-600 font-bold">G</span>
                    </div>
                    <div>
                      <h4 className="font-medium">Google OAuth</h4>
                      <p className="text-sm text-gray-500">Enable single sign-on with Google</p>
                    </div>
                  </div>
                  <Badge variant={formData.integration_google_oauth ? 'success' : 'default'}>
                    {formData.integration_google_oauth ? (
                      <><CheckCircle className="w-3 h-3 mr-1" /> Enabled</>
                    ) : (
                      <><XCircle className="w-3 h-3 mr-1" /> Disabled</>
                    )}
                  </Badge>
                </div>
                <div className="mt-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.integration_google_oauth}
                      onChange={(e) => updateField('integration_google_oauth', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm">Enable Google OAuth</span>
                  </label>
                </div>
              </div>

              {/* SMS Provider */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <span className="text-green-600 font-bold">SMS</span>
                  </div>
                  <div>
                    <h4 className="font-medium">SMS Provider</h4>
                    <p className="text-sm text-gray-500">Configure SMS notification service</p>
                  </div>
                </div>
                <Select
                  value={formData.integration_sms_provider}
                  onChange={(e) => updateField('integration_sms_provider', e.target.value)}
                  options={[
                    { value: 'twilio', label: 'Twilio' },
                    { value: 'aws_sns', label: 'AWS SNS' },
                    { value: 'nexmo', label: 'Nexmo/Vonage' },
                    { value: 'disabled', label: 'Disabled' },
                  ]}
                />
              </div>

              {/* Email Service */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-blue-600 font-bold">@</span>
                  </div>
                  <div>
                    <h4 className="font-medium">Email Service</h4>
                    <p className="text-sm text-gray-500">Configure email notification service</p>
                  </div>
                </div>
                <Select
                  value={formData.integration_email_service}
                  onChange={(e) => updateField('integration_email_service', e.target.value)}
                  options={[
                    { value: 'smtp', label: 'SMTP' },
                    { value: 'sendgrid', label: 'SendGrid' },
                    { value: 'aws_ses', label: 'AWS SES' },
                    { value: 'mailgun', label: 'Mailgun' },
                    { value: 'disabled', label: 'Disabled' },
                  ]}
                />
              </div>
            </CardContent>
          </Card>
        )}
      </form>

      {/* Last Updated Info */}
      {settings && (
        <Card className="bg-gray-50">
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">
              Last updated: {new Date(settings.updated_at).toLocaleString()}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
