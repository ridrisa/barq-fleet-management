import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Save, RotateCcw, Settings as SettingsIcon, Clock, MapPin, DollarSign, Bell } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { operationsSettingsAPI } from '@/lib/api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export default function OperationsSettings() {
  useTranslation()
  const queryClient = useQueryClient()

  const { data: settings, isLoading } = useQuery({
    queryKey: ['operations-settings'],
    queryFn: operationsSettingsAPI.getAll,
  })

  const updateMutation = useMutation({
    mutationFn: operationsSettingsAPI.update,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operations-settings'] })
      alert('Settings saved successfully!')
    },
    onError: () => {
      alert('Failed to save settings')
    },
  })

  const resetMutation = useMutation({
    mutationFn: operationsSettingsAPI.reset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operations-settings'] })
      alert('Settings reset to defaults!')
    },
  })

  const [formData, setFormData] = useState({
    // Delivery Settings
    delivery_time_slots: ['morning', 'afternoon', 'evening'],
    default_delivery_duration: 30,
    max_deliveries_per_courier: 25,
    enable_express_delivery: true,

    // Zone Settings
    default_zone_capacity: 100,
    auto_assign_to_nearest_zone: true,
    default_coverage_radius: 15,

    // COD Settings
    cod_collection_limit: 5000,
    cod_reconciliation_frequency: 'daily',
    enable_cod: true,

    // Priority Rules
    express_sla_hours: 2,
    same_day_sla_hours: 8,
    standard_sla_hours: 24,

    // Notification Settings
    notify_on_new_delivery: true,
    notify_on_status_change: true,
    notify_on_sla_breach: true,
    enable_sms_notifications: false,
  })

  const handleChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  const handleReset = async () => {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      resetMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  // Use fetched settings or form data
  const currentSettings = settings || formData

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Operations Settings</h1>
        <Button variant="outline" onClick={handleReset} disabled={resetMutation.isPending}>
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset to Defaults
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Delivery Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              Delivery Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Delivery Duration (minutes)
                </label>
                <Input
                  type="number"
                  value={currentSettings.default_delivery_duration || formData.default_delivery_duration}
                  onChange={(e) => handleChange('default_delivery_duration', parseInt(e.target.value))}
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Deliveries Per Courier Per Day
                </label>
                <Input
                  type="number"
                  value={currentSettings.max_deliveries_per_courier || formData.max_deliveries_per_courier}
                  onChange={(e) => handleChange('max_deliveries_per_courier', parseInt(e.target.value))}
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Delivery Time Slots
              </label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={(currentSettings.delivery_time_slots || formData.delivery_time_slots).includes('morning')}
                    onChange={(e) => {
                      const slots = currentSettings.delivery_time_slots || formData.delivery_time_slots
                      handleChange(
                        'delivery_time_slots',
                        e.target.checked ? [...slots, 'morning'] : slots.filter((s: string) => s !== 'morning')
                      )
                    }}
                    className="rounded"
                  />
                  <span>Morning (8AM-12PM)</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={(currentSettings.delivery_time_slots || formData.delivery_time_slots).includes('afternoon')}
                    onChange={(e) => {
                      const slots = currentSettings.delivery_time_slots || formData.delivery_time_slots
                      handleChange(
                        'delivery_time_slots',
                        e.target.checked ? [...slots, 'afternoon'] : slots.filter((s: string) => s !== 'afternoon')
                      )
                    }}
                    className="rounded"
                  />
                  <span>Afternoon (12PM-5PM)</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={(currentSettings.delivery_time_slots || formData.delivery_time_slots).includes('evening')}
                    onChange={(e) => {
                      const slots = currentSettings.delivery_time_slots || formData.delivery_time_slots
                      handleChange(
                        'delivery_time_slots',
                        e.target.checked ? [...slots, 'evening'] : slots.filter((s: string) => s !== 'evening')
                      )
                    }}
                    className="rounded"
                  />
                  <span>Evening (5PM-9PM)</span>
                </label>
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={currentSettings.enable_express_delivery ?? formData.enable_express_delivery}
                  onChange={(e) => handleChange('enable_express_delivery', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm font-medium text-gray-700">Enable Express Delivery</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Zone Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-green-600" />
              Zone Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Zone Capacity
                </label>
                <Input
                  type="number"
                  value={currentSettings.default_zone_capacity || formData.default_zone_capacity}
                  onChange={(e) => handleChange('default_zone_capacity', parseInt(e.target.value))}
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Coverage Radius (km)
                </label>
                <Input
                  type="number"
                  step="0.1"
                  value={currentSettings.default_coverage_radius || formData.default_coverage_radius}
                  onChange={(e) => handleChange('default_coverage_radius', parseFloat(e.target.value))}
                  min="0.1"
                />
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={currentSettings.auto_assign_to_nearest_zone ?? formData.auto_assign_to_nearest_zone}
                  onChange={(e) => handleChange('auto_assign_to_nearest_zone', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm font-medium text-gray-700">Auto-assign Deliveries to Nearest Zone</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* COD Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-purple-600" />
              COD Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  COD Collection Limit Per Delivery (SAR)
                </label>
                <Input
                  type="number"
                  value={currentSettings.cod_collection_limit || formData.cod_collection_limit}
                  onChange={(e) => handleChange('cod_collection_limit', parseFloat(e.target.value))}
                  min="0"
                  step="100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  COD Reconciliation Frequency
                </label>
                <Select
                  value={currentSettings.cod_reconciliation_frequency || formData.cod_reconciliation_frequency}
                  onChange={(e) => handleChange('cod_reconciliation_frequency', e.target.value)}
                  options={[
                    { value: 'daily', label: 'Daily' },
                    { value: 'weekly', label: 'Weekly' },
                    { value: 'biweekly', label: 'Bi-weekly' },
                    { value: 'monthly', label: 'Monthly' },
                  ]}
                />
              </div>
            </div>

            <div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={currentSettings.enable_cod ?? formData.enable_cod}
                  onChange={(e) => handleChange('enable_cod', e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm font-medium text-gray-700">Enable COD (Cash on Delivery)</span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Priority Rules */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SettingsIcon className="h-5 w-5 text-orange-600" />
              Priority SLA Rules
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Express SLA (hours)
                </label>
                <Input
                  type="number"
                  value={currentSettings.express_sla_hours || formData.express_sla_hours}
                  onChange={(e) => handleChange('express_sla_hours', parseInt(e.target.value))}
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Same-Day SLA (hours)
                </label>
                <Input
                  type="number"
                  value={currentSettings.same_day_sla_hours || formData.same_day_sla_hours}
                  onChange={(e) => handleChange('same_day_sla_hours', parseInt(e.target.value))}
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Standard SLA (hours)
                </label>
                <Input
                  type="number"
                  value={currentSettings.standard_sla_hours || formData.standard_sla_hours}
                  onChange={(e) => handleChange('standard_sla_hours', parseInt(e.target.value))}
                  min="1"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-yellow-600" />
              Notification Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={currentSettings.notify_on_new_delivery ?? formData.notify_on_new_delivery}
                onChange={(e) => handleChange('notify_on_new_delivery', e.target.checked)}
                className="rounded"
              />
              <span className="text-sm font-medium text-gray-700">Notify on New Delivery</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={currentSettings.notify_on_status_change ?? formData.notify_on_status_change}
                onChange={(e) => handleChange('notify_on_status_change', e.target.checked)}
                className="rounded"
              />
              <span className="text-sm font-medium text-gray-700">Notify on Status Change</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={currentSettings.notify_on_sla_breach ?? formData.notify_on_sla_breach}
                onChange={(e) => handleChange('notify_on_sla_breach', e.target.checked)}
                className="rounded"
              />
              <span className="text-sm font-medium text-gray-700">Notify on SLA Breach</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={currentSettings.enable_sms_notifications ?? formData.enable_sms_notifications}
                onChange={(e) => handleChange('enable_sms_notifications', e.target.checked)}
                className="rounded"
              />
              <span className="text-sm font-medium text-gray-700">Enable SMS Notifications</span>
            </label>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end gap-4">
          <Button type="submit" disabled={updateMutation.isPending}>
            <Save className="h-4 w-4 mr-2" />
            {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>
      </form>
    </div>
  )
}
