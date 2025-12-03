import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useOrganization } from '@/contexts/OrganizationContext'
import { organizationAPI } from '@/lib/api'
import { Building2, Users, Settings, Save, Crown, UserPlus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface OrganizationMember {
  id: number
  user_id: number
  email: string
  full_name: string
  role: 'OWNER' | 'ADMIN' | 'MANAGER' | 'VIEWER'
  is_active: boolean
  created_at: string
}

export default function OrganizationSettings() {
  const queryClient = useQueryClient()
  const { organization: currentOrganization, isOwnerOrAdmin } = useOrganization()
  const [activeTab, setActiveTab] = useState<'general' | 'members' | 'billing'>('general')

  // Organization form state
  const [orgForm, setOrgForm] = useState({
    name: '',
    settings: {
      default_language: 'en',
      timezone: 'UTC',
      currency: 'SAR',
      date_format: 'DD/MM/YYYY',
    },
  })

  // Invite form state
  const [inviteForm, setInviteForm] = useState({
    email: '',
    role: 'VIEWER' as 'ADMIN' | 'MANAGER' | 'VIEWER',
  })

  // Fetch organization details
  const { data: organization, isLoading } = useQuery({
    queryKey: ['organization', currentOrganization?.id],
    queryFn: () => organizationAPI.get(currentOrganization!.id),
    enabled: !!currentOrganization?.id,
  })

  // Fetch organization members
  const { data: members = [], isLoading: membersLoading } = useQuery({
    queryKey: ['organization-members', currentOrganization?.id],
    queryFn: () => organizationAPI.getMembers(currentOrganization!.id),
    enabled: !!currentOrganization?.id,
  })

  // Update form when organization data loads
  useEffect(() => {
    if (organization) {
      setOrgForm({
        name: organization.name,
        settings: {
          default_language: organization.settings?.default_language || 'en',
          timezone: organization.settings?.timezone || 'UTC',
          currency: organization.settings?.currency || 'SAR',
          date_format: organization.settings?.date_format || 'DD/MM/YYYY',
        },
      })
    }
  }, [organization])

  // Update organization mutation
  const updateOrgMutation = useMutation({
    mutationFn: (data: typeof orgForm) => organizationAPI.update(currentOrganization!.id, data),
    onSuccess: () => {
      toast.success('Organization updated successfully')
      queryClient.invalidateQueries({ queryKey: ['organization', currentOrganization?.id] })
    },
    onError: () => {
      toast.error('Failed to update organization')
    },
  })

  // Invite member mutation
  const inviteMemberMutation = useMutation({
    mutationFn: (data: typeof inviteForm) =>
      organizationAPI.inviteMember(currentOrganization!.id, data),
    onSuccess: () => {
      toast.success('Invitation sent successfully')
      setInviteForm({ email: '', role: 'VIEWER' })
      queryClient.invalidateQueries({ queryKey: ['organization-members', currentOrganization?.id] })
    },
    onError: () => {
      toast.error('Failed to send invitation')
    },
  })

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: (userId: number) =>
      organizationAPI.removeMember(currentOrganization!.id, userId),
    onSuccess: () => {
      toast.success('Member removed successfully')
      queryClient.invalidateQueries({ queryKey: ['organization-members', currentOrganization?.id] })
    },
    onError: () => {
      toast.error('Failed to remove member')
    },
  })

  // Update member role mutation
  const updateMemberRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: number; role: string }) =>
      organizationAPI.updateMemberRole(currentOrganization!.id, userId, role),
    onSuccess: () => {
      toast.success('Member role updated')
      queryClient.invalidateQueries({ queryKey: ['organization-members', currentOrganization?.id] })
    },
    onError: () => {
      toast.error('Failed to update member role')
    },
  })

  const handleOrgSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateOrgMutation.mutate(orgForm)
  }

  const handleInviteSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    inviteMemberMutation.mutate(inviteForm)
  }

  if (!currentOrganization) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">No organization selected</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  const tabs = [
    { id: 'general' as const, label: 'General', icon: Settings },
    { id: 'members' as const, label: 'Members', icon: Users },
    { id: 'billing' as const, label: 'Billing', icon: Building2 },
  ]

  const roleOptions = [
    { value: 'ADMIN', label: 'Admin' },
    { value: 'MANAGER', label: 'Manager' },
    { value: 'VIEWER', label: 'Viewer' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Organization Settings</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Building2 className="w-4 h-4" />
          {currentOrganization.name}
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

      {/* General Tab */}
      {activeTab === 'general' && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Organization Details</h3>
            <form onSubmit={handleOrgSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Organization Name</label>
                  <Input
                    value={orgForm.name}
                    onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value })}
                    disabled={!isOwnerOrAdmin}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Default Language</label>
                  <Select
                    value={orgForm.settings.default_language}
                    onChange={(e) =>
                      setOrgForm({
                        ...orgForm,
                        settings: { ...orgForm.settings, default_language: e.target.value },
                      })
                    }
                    disabled={!isOwnerOrAdmin}
                    options={[
                      { value: 'en', label: 'English' },
                      { value: 'ar', label: 'Arabic' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Timezone</label>
                  <Select
                    value={orgForm.settings.timezone}
                    onChange={(e) =>
                      setOrgForm({
                        ...orgForm,
                        settings: { ...orgForm.settings, timezone: e.target.value },
                      })
                    }
                    disabled={!isOwnerOrAdmin}
                    options={[
                      { value: 'UTC', label: 'UTC' },
                      { value: 'Asia/Riyadh', label: 'Asia/Riyadh (GMT+3)' },
                      { value: 'America/New_York', label: 'America/New_York (EST)' },
                      { value: 'Europe/London', label: 'Europe/London (GMT)' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Currency</label>
                  <Select
                    value={orgForm.settings.currency}
                    onChange={(e) =>
                      setOrgForm({
                        ...orgForm,
                        settings: { ...orgForm.settings, currency: e.target.value },
                      })
                    }
                    disabled={!isOwnerOrAdmin}
                    options={[
                      { value: 'SAR', label: 'SAR - Saudi Riyal' },
                      { value: 'USD', label: 'USD - US Dollar' },
                      { value: 'EUR', label: 'EUR - Euro' },
                      { value: 'GBP', label: 'GBP - British Pound' },
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Date Format</label>
                  <Select
                    value={orgForm.settings.date_format}
                    onChange={(e) =>
                      setOrgForm({
                        ...orgForm,
                        settings: { ...orgForm.settings, date_format: e.target.value },
                      })
                    }
                    disabled={!isOwnerOrAdmin}
                    options={[
                      { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
                      { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
                      { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' },
                    ]}
                  />
                </div>
              </div>

              {/* Subscription Info */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Subscription Plan</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Plan</p>
                    <p className="font-medium">{organization?.subscription_plan || 'FREE'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Status</p>
                    <p className="font-medium">{organization?.subscription_status || 'TRIAL'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Max Users</p>
                    <p className="font-medium">{organization?.max_users || 5}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Max Couriers</p>
                    <p className="font-medium">{organization?.max_couriers || 50}</p>
                  </div>
                </div>
              </div>

              {isOwnerOrAdmin && (
                <div className="flex justify-end">
                  <Button type="submit" disabled={updateOrgMutation.isPending}>
                    <Save className="w-4 h-4 mr-2" />
                    {updateOrgMutation.isPending ? 'Saving...' : 'Save Changes'}
                  </Button>
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      )}

      {/* Members Tab */}
      {activeTab === 'members' && (
        <div className="space-y-6">
          {/* Invite Member Form */}
          {isOwnerOrAdmin && (
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-lg font-semibold mb-4">Invite New Member</h3>
                <form onSubmit={handleInviteSubmit} className="flex gap-4">
                  <div className="flex-1">
                    <Input
                      type="email"
                      placeholder="Email address"
                      value={inviteForm.email}
                      onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="w-40">
                    <Select
                      value={inviteForm.role}
                      onChange={(e) =>
                        setInviteForm({
                          ...inviteForm,
                          role: e.target.value as 'ADMIN' | 'MANAGER' | 'VIEWER',
                        })
                      }
                      options={roleOptions}
                    />
                  </div>
                  <Button type="submit" disabled={inviteMemberMutation.isPending}>
                    <UserPlus className="w-4 h-4 mr-2" />
                    {inviteMemberMutation.isPending ? 'Inviting...' : 'Invite'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Members List */}
          <Card>
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold mb-4">Team Members</h3>
              {membersLoading ? (
                <div className="flex justify-center py-8">
                  <Spinner />
                </div>
              ) : (
                <div className="space-y-3">
                  {members.map((member: OrganizationMember) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <span className="text-blue-600 font-medium">
                            {member.full_name?.charAt(0) || member.email.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium flex items-center gap-2">
                            {member.full_name || member.email}
                            {member.role === 'OWNER' && (
                              <Crown className="w-4 h-4 text-yellow-500" />
                            )}
                          </p>
                          <p className="text-sm text-gray-500">{member.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {isOwnerOrAdmin && member.role !== 'OWNER' ? (
                          <>
                            <Select
                              value={member.role}
                              onChange={(e) =>
                                updateMemberRoleMutation.mutate({
                                  userId: member.user_id,
                                  role: e.target.value,
                                })
                              }
                              options={roleOptions}
                              className="w-32"
                            />
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                if (confirm('Are you sure you want to remove this member?')) {
                                  removeMemberMutation.mutate(member.user_id)
                                }
                              }}
                              className="text-red-600 hover:bg-red-50"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </>
                        ) : (
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              member.role === 'OWNER'
                                ? 'bg-yellow-100 text-yellow-700'
                                : member.role === 'ADMIN'
                                  ? 'bg-blue-100 text-blue-700'
                                  : member.role === 'MANAGER'
                                    ? 'bg-green-100 text-green-700'
                                    : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {member.role}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Billing Tab */}
      {activeTab === 'billing' && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Billing & Subscription</h3>
            <div className="space-y-6">
              {/* Current Plan */}
              <div className="p-6 border rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="text-xl font-bold text-gray-900">
                      {organization?.subscription_plan || 'FREE'} Plan
                    </h4>
                    <p className="text-gray-600">
                      {organization?.subscription_status === 'TRIAL'
                        ? `Trial ends ${organization?.trial_ends_at ? new Date(organization.trial_ends_at).toLocaleDateString() : 'soon'}`
                        : `Status: ${organization?.subscription_status || 'Active'}`}
                    </p>
                  </div>
                  {isOwnerOrAdmin && (
                    <Button variant="outline">Upgrade Plan</Button>
                  )}
                </div>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {organization?.max_users || 5}
                    </p>
                    <p className="text-sm text-gray-500">Users</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {organization?.max_couriers || 50}
                    </p>
                    <p className="text-sm text-gray-500">Couriers</p>
                  </div>
                  <div className="p-3 bg-white rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {organization?.max_vehicles || 25}
                    </p>
                    <p className="text-sm text-gray-500">Vehicles</p>
                  </div>
                </div>
              </div>

              {/* Plan Comparison */}
              <div>
                <h4 className="font-medium mb-4">Available Plans</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    {
                      name: 'Basic',
                      price: '$49',
                      users: 10,
                      couriers: 100,
                      vehicles: 50,
                    },
                    {
                      name: 'Professional',
                      price: '$149',
                      users: 50,
                      couriers: 500,
                      vehicles: 250,
                      popular: true,
                    },
                    {
                      name: 'Enterprise',
                      price: 'Custom',
                      users: 'Unlimited',
                      couriers: 'Unlimited',
                      vehicles: 'Unlimited',
                    },
                  ].map((plan) => (
                    <div
                      key={plan.name}
                      className={`p-4 border rounded-lg ${
                        plan.popular ? 'border-blue-500 ring-2 ring-blue-200' : ''
                      }`}
                    >
                      {plan.popular && (
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
                          Most Popular
                        </span>
                      )}
                      <h5 className="text-lg font-bold mt-2">{plan.name}</h5>
                      <p className="text-2xl font-bold text-blue-600 mb-4">
                        {plan.price}
                        {plan.price !== 'Custom' && (
                          <span className="text-sm text-gray-500">/month</span>
                        )}
                      </p>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li>Up to {plan.users} users</li>
                        <li>Up to {plan.couriers} couriers</li>
                        <li>Up to {plan.vehicles} vehicles</li>
                      </ul>
                      {isOwnerOrAdmin && (
                        <Button variant="outline" className="w-full mt-4">
                          {plan.name === organization?.subscription_plan ? 'Current' : 'Select'}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
