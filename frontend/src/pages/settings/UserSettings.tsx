import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { authAPI, profileAPI } from '@/lib/api'
import { Save, Shield, User, Mail, Phone, Key, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function UserSettings() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'account' | 'security' | 'advanced'>('account')
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [sessionTimeout, setSessionTimeout] = useState(30)
  const [apiAccessEnabled, setApiAccessEnabled] = useState(false)

  // Account form state
  const [accountForm, setAccountForm] = useState({
    username: '',
    email: '',
    phone: '',
    role: '',
  })

  // Fetch current user data
  const { data: currentUser, isLoading } = useQuery({
    queryKey: ['current-user'],
    queryFn: authAPI.getCurrentUser,
  })

  // Update form when user data loads
  useEffect(() => {
    if (currentUser) {
      setAccountForm({
        username: currentUser.username || currentUser.email,
        email: currentUser.email,
        phone: currentUser.phone || '',
        role: currentUser.role || 'user',
      })
    }
  }, [currentUser])

  // Update account mutation
  const updateAccountMutation = useMutation({
    mutationFn: profileAPI.update,
    onSuccess: () => {
      toast.success('Account settings updated successfully')
      queryClient.invalidateQueries({ queryKey: ['current-user'] })
    },
    onError: () => {
      toast.error('Failed to update account settings')
    },
  })

  const handleAccountSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateAccountMutation.mutate({
      email: accountForm.email,
      phone: accountForm.phone,
    })
  }

  const handleEnableTwoFactor = () => {
    if (!twoFactorEnabled) {
      toast.success('Two-factor authentication setup initiated. Check your email for instructions.')
      setTwoFactorEnabled(true)
    } else {
      if (window.confirm('Are you sure you want to disable two-factor authentication?')) {
        setTwoFactorEnabled(false)
        toast.success('Two-factor authentication disabled')
      }
    }
  }

  const handleDeleteAccount = () => {
    const confirmation = window.prompt(
      'This action cannot be undone. Type "DELETE" to confirm account deletion:'
    )
    if (confirmation === 'DELETE') {
      toast.error('Account deletion is not available in this demo')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  const tabs = [
    { id: 'account' as const, label: 'Account', icon: User },
    { id: 'security' as const, label: 'Security', icon: Shield },
    { id: 'advanced' as const, label: 'Advanced', icon: Key },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">User Account Settings</h1>
          <p className="text-gray-600 mt-1">Manage your account preferences and security settings</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Account Tab */}
      {activeTab === 'account' && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Account Information</h3>
            <form onSubmit={handleAccountSubmit} className="space-y-4 max-w-xl">
              <div>
                <label className="block text-sm font-medium mb-2">Username</label>
                <Input
                  value={accountForm.username}
                  disabled
                  leftIcon={<User className="w-4 h-4 text-gray-400" />}
                  helperText="Username cannot be changed"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Email Address</label>
                <Input
                  type="email"
                  value={accountForm.email}
                  onChange={(e) =>
                    setAccountForm({ ...accountForm, email: e.target.value })
                  }
                  leftIcon={<Mail className="w-4 h-4 text-gray-400" />}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Phone Number</label>
                <Input
                  value={accountForm.phone}
                  onChange={(e) =>
                    setAccountForm({ ...accountForm, phone: e.target.value })
                  }
                  leftIcon={<Phone className="w-4 h-4 text-gray-400" />}
                  placeholder="+966 50 123 4567"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Role</label>
                <Input
                  value={accountForm.role}
                  disabled
                  helperText="Contact administrator to change your role"
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" disabled={updateAccountMutation.isPending}>
                  <Save className="w-4 h-4 mr-2" />
                  {updateAccountMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-6">
          {/* Two-Factor Authentication */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Two-Factor Authentication</h3>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-gray-700 mb-2">
                    Add an extra layer of security to your account by requiring a code in addition to your password.
                  </p>
                  <p className="text-sm text-gray-500">
                    Status:{' '}
                    <span
                      className={`font-medium ${
                        twoFactorEnabled ? 'text-green-600' : 'text-gray-600'
                      }`}
                    >
                      {twoFactorEnabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </p>
                </div>
                <Button
                  variant={twoFactorEnabled ? 'danger' : 'primary'}
                  onClick={handleEnableTwoFactor}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  {twoFactorEnabled ? 'Disable' : 'Enable'} 2FA
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Session Management */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Session Management</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Session Timeout (minutes)
                  </label>
                  <Input
                    type="number"
                    value={sessionTimeout}
                    onChange={(e) => setSessionTimeout(parseInt(e.target.value))}
                    min={5}
                    max={1440}
                    helperText="Automatically log out after this many minutes of inactivity"
                  />
                </div>
                <div className="pt-4 border-t">
                  <Button variant="outline">
                    <Key className="w-4 h-4 mr-2" />
                    View Active Sessions
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Password Security */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Password Security</h3>
              <div className="space-y-3">
                <p className="text-sm text-gray-600">
                  Last password change:{' '}
                  <span className="font-medium">
                    {currentUser?.password_changed_at
                      ? new Date(currentUser.password_changed_at).toLocaleDateString()
                      : 'Never'}
                  </span>
                </p>
                <Button variant="outline" onClick={() => window.location.href = '/settings/profile'}>
                  <Key className="w-4 h-4 mr-2" />
                  Change Password
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Advanced Tab */}
      {activeTab === 'advanced' && (
        <div className="space-y-6">
          {/* API Access */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">API Access</h3>
              <div className="space-y-4">
                <label className="flex items-center justify-between p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <div>
                    <p className="font-medium">Enable API Access</p>
                    <p className="text-sm text-gray-500">
                      Allow programmatic access to your account via API keys
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={apiAccessEnabled}
                    onChange={(e) => setApiAccessEnabled(e.target.checked)}
                    className="w-5 h-5 text-blue-600"
                  />
                </label>
                {apiAccessEnabled && (
                  <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-900">
                      Visit the API Keys section in Admin panel to generate and manage your API keys.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Data Export */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Data Export</h3>
              <p className="text-gray-600 mb-4">
                Download a copy of your personal data including profile information, activity logs, and settings.
              </p>
              <Button variant="outline">
                <Save className="w-4 h-4 mr-2" />
                Request Data Export
              </Button>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-red-200">
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold text-red-600 mb-4">Danger Zone</h3>
              <div className="space-y-4">
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="font-medium text-red-900 mb-2">Delete Account</h4>
                  <p className="text-sm text-red-800 mb-3">
                    Once you delete your account, there is no going back. This action is permanent and cannot be undone.
                  </p>
                  <Button variant="danger" onClick={handleDeleteAccount}>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete My Account
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
