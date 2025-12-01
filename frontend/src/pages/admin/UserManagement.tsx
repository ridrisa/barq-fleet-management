import { useState } from 'react'
import { Plus, Search, Mail, Key, Power, PowerOff, Trash2, Activity } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { adminUsersAPI, rolesAPI } from '@/lib/adminAPI'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { UserForm, UserFormData } from '@/components/forms/UserForm'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  department?: string
  phone?: string
  is_active: boolean
  created_at: string
  last_login?: string
}

interface ActivityLog {
  id: number
  action: string
  timestamp: string
  ip_address: string
  user_agent: string
}

export default function UserManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [showActivityModal, setShowActivityModal] = useState(false)
  const [selectedUserForLogs, setSelectedUserForLogs] = useState<number | null>(null)
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const queryClient = useQueryClient()

  // Use the reusable data table hook
  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
  } = useDataTable({
    queryKey: 'admin-users',
    queryFn: adminUsersAPI.getAll,
    pageSize: 10,
    searchFields: ['email', 'full_name', 'department'],
  })

  // Fetch roles for filter
  const { data: roles } = useQuery({
    queryKey: ['roles'],
    queryFn: () => rolesAPI.getAll(),
  })

  // Fetch activity logs for selected user
  const { data: activityLogs } = useQuery({
    queryKey: ['activity-logs', selectedUserForLogs],
    queryFn: () =>
      selectedUserForLogs ? adminUsersAPI.getActivityLogs(selectedUserForLogs) : Promise.resolve([]),
    enabled: !!selectedUserForLogs,
  })

  // Use the reusable CRUD hook
  const { handleCreate, handleUpdate, handleDelete } = useCRUD({
    queryKey: 'admin-users',
    entityName: 'User',
    create: adminUsersAPI.create as (data: UserFormData) => Promise<User>,
    update: adminUsersAPI.update as (id: number, data: Partial<UserFormData>) => Promise<User>,
    delete: adminUsersAPI.delete,
  })

  // Reset password mutation
  const resetPasswordMutation = useMutation({
    mutationFn: (userId: number) => adminUsersAPI.resetPassword(userId),
    onSuccess: () => {
      alert('Password reset email sent successfully')
    },
    onError: () => {
      alert('Failed to send password reset email')
    },
  })

  // Toggle active status
  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      adminUsersAPI.update(id, { is_active } as Parameters<typeof adminUsersAPI.update>[1]),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => {
      alert('Failed to update user status')
    },
  })

  const handleFormSubmit = async (data: UserFormData) => {
    try {
      if (editingUser) {
        await handleUpdate(editingUser.id, data)
      } else {
        await handleCreate(data)
      }
      setIsModalOpen(false)
      setEditingUser(null)
    } catch (_error: unknown) {
      // Error handled by useCRUD
    }
  }

  const handleEdit = (user: User) => {
    setEditingUser(user)
    setIsModalOpen(true)
  }

  const handleResetPassword = (userId: number) => {
    if (confirm('Send password reset email to this user?')) {
      resetPasswordMutation.mutate(userId)
    }
  }

  const handleToggleActive = (user: User) => {
    const action = user.is_active ? 'deactivate' : 'activate'
    if (confirm(`Are you sure you want to ${action} this user?`)) {
      toggleActiveMutation.mutate({ id: user.id, is_active: !user.is_active })
    }
  }

  const handleViewActivity = (userId: number) => {
    setSelectedUserForLogs(userId)
    setShowActivityModal(true)
  }

  // Filter data by role and status
  const typedData = filteredData as User[]
  const finalFilteredData = typedData.filter((user) => {
    const roleMatch = !roleFilter || user.role === roleFilter
    const statusMatch = !statusFilter || user.is_active.toString() === statusFilter
    return roleMatch && statusMatch
  })

  // Recalculate pagination based on filtered data
  const finalTotalPages = Math.ceil(finalFilteredData.length / pageSize)
  const finalPaginatedData = finalFilteredData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  // Calculate KPI metrics
  const totalUsers = finalFilteredData.length
  const activeUsers = finalFilteredData.filter((u) => u.is_active).length
  const inactiveUsers = totalUsers - activeUsers
  const admins = finalFilteredData.filter((u) => u.role === 'admin').length

  const columns = [
    {
      key: 'full_name',
      header: 'Name',
      sortable: true,
      render: (row: User) => (
        <div>
          <div className="font-medium text-gray-900">{row.full_name || 'N/A'}</div>
          <div className="text-sm text-gray-500">{row.email}</div>
        </div>
      ),
    },
    {
      key: 'role',
      header: 'Role',
      render: (row: User) => (
        <Badge variant="default">{row.role}</Badge>
      ),
    },
    {
      key: 'department',
      header: 'Department',
      render: (row: User) => row.department || '-',
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (row: User) => (
        <Badge variant={row.is_active ? 'success' : 'danger'}>
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'last_login',
      header: 'Last Login',
      render: (row: User) => {
        if (!row.last_login) return 'Never'
        return new Date(row.last_login).toLocaleString()
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: User) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleEdit(row)}
            title="Edit User"
          >
            <Mail className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleResetPassword(row.id)}
            title="Reset Password"
          >
            <Key className="h-4 w-4 text-yellow-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleToggleActive(row)}
            title={row.is_active ? 'Deactivate' : 'Activate'}
          >
            {row.is_active ? (
              <PowerOff className="h-4 w-4 text-red-600" />
            ) : (
              <Power className="h-4 w-4 text-green-600" />
            )}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleViewActivity(row.id)}
            title="View Activity"
          >
            <Activity className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete User"
          >
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading users: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">User Management</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage users, roles, and permissions. Control access to the system.
          </p>
        </div>
        <Button onClick={() => { setEditingUser(null); setIsModalOpen(true) }}>
          <Plus className="h-4 w-4 mr-2" />
          New User
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{totalUsers}</p>
              <p className="text-sm text-gray-600">Total Users</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{activeUsers}</p>
              <p className="text-sm text-gray-600">Active Users</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{inactiveUsers}</p>
              <p className="text-sm text-gray-600">Inactive Users</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{admins}</p>
              <p className="text-sm text-gray-600">Admins</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          {/* Filters */}
          <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              placeholder="Search by name, email, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
            <Select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              options={[
                { value: '', label: 'All Roles' },
                ...(roles?.map((r: { name: string }) => ({ value: r.name, label: r.name })) || []),
              ]}
            />
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: '', label: 'All Status' },
                { value: 'true', label: 'Active' },
                { value: 'false', label: 'Inactive' },
              ]}
            />
          </div>

          <Table data={finalPaginatedData} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={finalTotalPages}
            onPageChange={setCurrentPage}
            totalItems={finalFilteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* User Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingUser(null)
        }}
        title={editingUser ? 'Edit User' : 'Create New User'}
        size="lg"
      >
        <UserForm
          initialData={editingUser || undefined}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsModalOpen(false)
            setEditingUser(null)
          }}
          mode={editingUser ? 'edit' : 'create'}
        />
      </Modal>

      {/* Activity Logs Modal */}
      <Modal
        isOpen={showActivityModal}
        onClose={() => {
          setShowActivityModal(false)
          setSelectedUserForLogs(null)
        }}
        title="User Activity Logs"
        size="lg"
      >
        <div className="mt-4">
          {activityLogs && activityLogs.length > 0 ? (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {activityLogs.map((log: ActivityLog) => (
                <Card key={log.id}>
                  <CardContent className="pt-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{log.action}</p>
                        <p className="text-sm text-gray-500 mt-1">
                          {new Date(log.timestamp).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">IP: {log.ip_address}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No activity logs found</p>
          )}
        </div>
      </Modal>

      {/* Security Notice */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <h3 className="text-sm font-semibold text-yellow-900">Security Reminder</h3>
        <p className="mt-2 text-sm text-yellow-800">
          Only grant admin privileges to trusted users. All user actions are logged and monitored.
          Inactive users are automatically logged out after 15 minutes.
        </p>
      </div>
    </div>
  )
}
