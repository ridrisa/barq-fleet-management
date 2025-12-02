import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { settingsAPI } from '@/lib/api'
import { Save, Building, Globe, Clock, DollarSign } from 'lucide-react'
import toast from 'react-hot-toast'

export default function GeneralSettings() {
  const queryClient = useQueryClient()

  // Fetch general settings
  const { data: settings, isLoading } = useQuery({
    queryKey: ['general-settings'],
    queryFn: settingsAPI.getGeneral,
  })

  // Local form state
  const [formData, setFormData] = useState({
    company_name: settings?.company_name || '',
    company_email: settings?.company_email || '',
    company_phone: settings?.company_phone || '',
    timezone: settings?.timezone || 'UTC',
    language: settings?.language || 'en',
    date_format: settings?.date_format || 'YYYY-MM-DD',
    time_format: settings?.time_format || '24h',
    currency: settings?.currency || 'USD',
    currency_symbol: settings?.currency_symbol || '$',
  })

  // Update whenever settings data changes
  useEffect(() => {
    if (settings) {
      setFormData({
        company_name: settings.company_name || '',
        company_email: settings.company_email || '',
        company_phone: settings.company_phone || '',
        timezone: settings.timezone || 'UTC',
        language: settings.language || 'en',
        date_format: settings.date_format || 'YYYY-MM-DD',
        time_format: settings.time_format || '24h',
        currency: settings.currency || 'USD',
        currency_symbol: settings.currency_symbol || '$',
      })
    }
  }, [settings])

  // Update settings mutation
  const updateMutation = useMutation({
    mutationFn: settingsAPI.updateGeneral,
    onSuccess: () => {
      toast.success('Settings updated successfully')
      queryClient.invalidateQueries({ queryKey: ['general-settings'] })
    },
    onError: () => {
      toast.error('Failed to update settings')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">General Settings</h1>
        <p className="text-gray-600">Manage your company information and preferences</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Company Information */}
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Building className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold">Company Information</h2>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Company Name</label>
              <Input
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                placeholder="BARQ Fleet Management"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Company Email</label>
                <Input
                  type="email"
                  value={formData.company_email}
                  onChange={(e) => setFormData({ ...formData, company_email: e.target.value })}
                  placeholder="info@barq-fleet.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Company Phone</label>
                <Input
                  value={formData.company_phone}
                  onChange={(e) => setFormData({ ...formData, company_phone: e.target.value })}
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Localization */}
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Globe className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold">Localization</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Timezone</label>
                <Select
                  value={formData.timezone}
                  onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                  options={[
                    { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
                    { value: 'America/New_York', label: 'Eastern Time (ET)' },
                    { value: 'America/Chicago', label: 'Central Time (CT)' },
                    { value: 'America/Denver', label: 'Mountain Time (MT)' },
                    { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
                    { value: 'Europe/London', label: 'London (GMT)' },
                    { value: 'Europe/Paris', label: 'Paris (CET)' },
                    { value: 'Asia/Dubai', label: 'Dubai (GST)' },
                    { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Language</label>
                <Select
                  value={formData.language}
                  onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                  options={[
                    { value: 'en', label: 'English' },
                    { value: 'ar', label: 'Arabic' },
                    { value: 'es', label: 'Spanish' },
                    { value: 'fr', label: 'French' },
                    { value: 'de', label: 'German' },
                  ]}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Date & Time Format */}
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold">Date & Time Format</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Date Format</label>
                <Select
                  value={formData.date_format}
                  onChange={(e) => setFormData({ ...formData, date_format: e.target.value })}
                  options={[
                    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2025-11-06)' },
                    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (06/11/2025)' },
                    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (11/06/2025)' },
                    { value: 'DD MMM YYYY', label: 'DD MMM YYYY (06 Nov 2025)' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Time Format</label>
                <Select
                  value={formData.time_format}
                  onChange={(e) => setFormData({ ...formData, time_format: e.target.value })}
                  options={[
                    { value: '24h', label: '24 Hour (14:30)' },
                    { value: '12h', label: '12 Hour (2:30 PM)' },
                  ]}
                />
              </div>
            </div>

            <div className="p-3 bg-gray-50 rounded-md text-sm">
              <strong>Preview:</strong> Current Date & Time:{' '}
              {new Date().toLocaleString('en-US', {
                timeZone: formData.timezone,
                year: 'numeric',
                month: 'short',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                hour12: formData.time_format === '12h',
              })}
            </div>
          </CardContent>
        </Card>

        {/* Currency */}
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <DollarSign className="w-5 h-5 text-gray-600" />
              <h2 className="text-lg font-semibold">Currency Settings</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Currency</label>
                <Select
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  options={[
                    { value: 'USD', label: 'US Dollar (USD)' },
                    { value: 'EUR', label: 'Euro (EUR)' },
                    { value: 'GBP', label: 'British Pound (GBP)' },
                    { value: 'SAR', label: 'Saudi Riyal (SAR)' },
                    { value: 'SAR', label: 'Saudi Riyal (SAR)' },
                    { value: 'JPY', label: 'Japanese Yen (JPY)' },
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Currency Symbol</label>
                <Input
                  value={formData.currency_symbol}
                  onChange={(e) => setFormData({ ...formData, currency_symbol: e.target.value })}
                  placeholder="$"
                />
              </div>
            </div>

            <div className="p-3 bg-gray-50 rounded-md text-sm">
              <strong>Preview:</strong> {formData.currency_symbol}1,234.56 {formData.currency}
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end gap-3">
          <Button type="button" variant="outline">
            Reset to Defaults
          </Button>
          <Button type="submit" disabled={updateMutation.isPending}>
            <Save className="w-4 h-4 mr-2" />
            {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </form>
    </div>
  )
}
