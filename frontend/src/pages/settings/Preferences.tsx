import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { preferencesAPI } from '@/lib/api'
import { Save, RotateCcw, Monitor, Globe, Calendar, DollarSign, Table } from 'lucide-react'
import toast from 'react-hot-toast'

interface Preferences {
  theme: 'light' | 'dark' | 'auto'
  language: 'en' | 'ar'
  date_format: string
  time_format: '12h' | '24h'
  currency: string
  default_page_size: number
  show_column_headers: boolean
  default_export_format: 'excel' | 'pdf' | 'csv'
  include_export_headers: boolean
}

const defaultPreferences: Preferences = {
  theme: 'light',
  language: 'en',
  date_format: 'DD/MM/YYYY',
  time_format: '24h',
  currency: 'SAR',
  default_page_size: 25,
  show_column_headers: true,
  default_export_format: 'excel',
  include_export_headers: true,
}

export default function Preferences() {
  const queryClient = useQueryClient()
  const [preferences, setPreferences] = useState<Preferences>(defaultPreferences)

  // Fetch preferences
  const { data: prefsData, isLoading } = useQuery({
    queryKey: ['preferences'],
    queryFn: preferencesAPI.get,
  })

  // Update state when data loads
  useEffect(() => {
    if (prefsData) {
      setPreferences(prefsData as Preferences)
    }
  }, [prefsData])

  // Update preferences mutation
  const updateMutation = useMutation({
    mutationFn: preferencesAPI.update,
    onSuccess: () => {
      toast.success('Preferences saved successfully')
      queryClient.invalidateQueries({ queryKey: ['preferences'] })
    },
    onError: () => {
      toast.error('Failed to save preferences')
    },
  })

  // Reset preferences mutation
  const resetMutation = useMutation({
    mutationFn: preferencesAPI.reset,
    onSuccess: () => {
      toast.success('Preferences reset to defaults')
      setPreferences(defaultPreferences)
      queryClient.invalidateQueries({ queryKey: ['preferences'] })
    },
    onError: () => {
      toast.error('Failed to reset preferences')
    },
  })

  const handleSave = () => {
    updateMutation.mutate(preferences)
  }

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all preferences to default values?')) {
      resetMutation.mutate()
    }
  }

  const handleThemeChange = (theme: 'light' | 'dark' | 'auto') => {
    setPreferences({ ...preferences, theme })

    // Apply theme immediately
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (theme === 'light') {
      document.documentElement.classList.remove('dark')
    } else {
      // Auto mode - use system preference
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  const sections = [
    {
      title: 'Display Settings',
      icon: Monitor,
      fields: [
        {
          label: 'Theme',
          value: preferences.theme,
          onChange: (value: string) => handleThemeChange(value as 'light' | 'dark' | 'auto'),
          options: [
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' },
            { value: 'auto', label: 'Auto (System)' },
          ],
        },
        {
          label: 'Language',
          value: preferences.language,
          onChange: (value: string) => setPreferences({ ...preferences, language: value as 'en' | 'ar' }),
          options: [
            { value: 'en', label: 'English' },
            { value: 'ar', label: 'Arabic (العربية)' },
          ],
        },
      ],
    },
    {
      title: 'Date & Time',
      icon: Calendar,
      fields: [
        {
          label: 'Date Format',
          value: preferences.date_format,
          onChange: (value: string) => setPreferences({ ...preferences, date_format: value }),
          options: [
            { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (31/12/2025)' },
            { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (12/31/2025)' },
            { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2025-12-31)' },
          ],
        },
        {
          label: 'Time Format',
          value: preferences.time_format,
          onChange: (value: string) => setPreferences({ ...preferences, time_format: value as '12h' | '24h' }),
          options: [
            { value: '12h', label: '12-hour (3:30 PM)' },
            { value: '24h', label: '24-hour (15:30)' },
          ],
        },
      ],
    },
    {
      title: 'Regional',
      icon: Globe,
      fields: [
        {
          label: 'Currency',
          value: preferences.currency,
          onChange: (value: string) => setPreferences({ ...preferences, currency: value }),
          options: [
            { value: 'SAR', label: 'SAR (Saudi Riyal)' },
            { value: 'USD', label: 'USD (US Dollar)' },
            { value: 'EUR', label: 'EUR (Euro)' },
            { value: 'GBP', label: 'GBP (British Pound)' },
          ],
        },
      ],
    },
    {
      title: 'Table Settings',
      icon: Table,
      fields: [
        {
          label: 'Default Page Size',
          value: preferences.default_page_size,
          onChange: (value: string) => setPreferences({ ...preferences, default_page_size: parseInt(value) }),
          options: [
            { value: '10', label: '10 rows' },
            { value: '25', label: '25 rows' },
            { value: '50', label: '50 rows' },
            { value: '100', label: '100 rows' },
          ],
        },
      ],
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Application Preferences</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset} disabled={resetMutation.isPending}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            <Save className="w-4 h-4 mr-2" />
            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {sections.map((section) => (
          <Card key={section.title}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-4">
                <section.icon className="w-5 h-5 text-blue-600" />
                <h3 className="text-lg font-semibold">{section.title}</h3>
              </div>
              <div className="space-y-4">
                {section.fields.map((field) => (
                  <div key={field.label} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <label className="text-sm font-medium">{field.label}</label>
                    <div className="md:col-span-2">
                      <Select
                        value={String(field.value)}
                        onChange={(e) => field.onChange(e.target.value)}
                        options={field.options}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Export Settings */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-4">
              <DollarSign className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-semibold">Export Settings</h3>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                <label className="text-sm font-medium">Default Export Format</label>
                <div className="md:col-span-2">
                  <Select
                    value={preferences.default_export_format}
                    onChange={(e) =>
                      setPreferences({
                        ...preferences,
                        default_export_format: e.target.value as 'excel' | 'pdf' | 'csv',
                      })
                    }
                    options={[
                      { value: 'excel', label: 'Excel (.xlsx)' },
                      { value: 'pdf', label: 'PDF (.pdf)' },
                      { value: 'csv', label: 'CSV (.csv)' },
                    ]}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                <label className="text-sm font-medium">Include Headers in Export</label>
                <div className="md:col-span-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.include_export_headers}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          include_export_headers: e.target.checked,
                        })
                      }
                      className="w-5 h-5 text-blue-600"
                    />
                    <span className="text-sm text-gray-600">
                      Include column headers when exporting data
                    </span>
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                <label className="text-sm font-medium">Show Column Headers</label>
                <div className="md:col-span-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences.show_column_headers}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          show_column_headers: e.target.checked,
                        })
                      }
                      className="w-5 h-5 text-blue-600"
                    />
                    <span className="text-sm text-gray-600">
                      Display column headers in tables
                    </span>
                  </label>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Preview Section */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold mb-4">Preview</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between p-3 bg-gray-50 rounded">
              <span className="text-gray-600">Date:</span>
              <span className="font-medium">
                {preferences.date_format === 'DD/MM/YYYY'
                  ? '31/12/2025'
                  : preferences.date_format === 'MM/DD/YYYY'
                  ? '12/31/2025'
                  : '2025-12-31'}
              </span>
            </div>
            <div className="flex justify-between p-3 bg-gray-50 rounded">
              <span className="text-gray-600">Time:</span>
              <span className="font-medium">
                {preferences.time_format === '12h' ? '3:30 PM' : '15:30'}
              </span>
            </div>
            <div className="flex justify-between p-3 bg-gray-50 rounded">
              <span className="text-gray-600">Currency:</span>
              <span className="font-medium">
                {preferences.currency === 'SAR'
                  ? 'SAR 1,234.56'
                  : preferences.currency === 'USD'
                  ? '$1,234.56'
                  : preferences.currency === 'EUR'
                  ? '€1,234.56'
                  : '£1,234.56'}
              </span>
            </div>
            <div className="flex justify-between p-3 bg-gray-50 rounded">
              <span className="text-gray-600">Language:</span>
              <span className="font-medium">
                {preferences.language === 'en' ? 'English' : 'العربية'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
