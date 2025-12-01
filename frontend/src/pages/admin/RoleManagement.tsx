import { useState } from 'react'
import { Plus, Edit, Trash2, Copy, Shield } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { rolesAPI, permissionsAPI } from '@/lib/adminAPI'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface Role {
  id: number
  name: string
  description: string
  level: number
  is_system: boolean
  created_at: string
}

interface Permission {
  id: number
  name: string
  resource: string
  action: string
  description: string
}

export default function RoleManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isPermissionModalOpen, setIsPermissionModalOpen] = useState(false)
  const [editingRole, setEditingRole] = useState<Role | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([])
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    level: 1,
  })

  const queryClient = useQueryClient()

  // Use the reusable data table hook
  const {
    isLoading,
    error,
    paginatedData: roles,
  } = useDataTable({
    queryKey: 'roles',
    queryFn: rolesAPI.getAll,
    pageSize: 100,
  })

  // Fetch all permissions
  const { data: permissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionsAPI.getAll(),
  })

  // Fetch role permissions when role is selected
  useQuery({
    queryKey: ['role-permissions', selectedRole?.id],
    queryFn: () => selectedRole ? permissionsAPI.getByRole(selectedRole.id) : Promise.resolve([]),
    enabled: !!selectedRole,
  })

  // Use the reusable CRUD hook
  const { handleCreate, handleUpdate, handleDelete } = useCRUD({
    queryKey: 'roles',
    entityName: 'Role',
    create: rolesAPI.create,
    update: rolesAPI.update,
    delete: rolesAPI.delete,
  })

  // Assign permissions mutation
  const assignPermissionsMutation = useMutation({
    mutationFn: ({ roleId, permissionIds }: { roleId: number; permissionIds: number[] }) =>
      permissionsAPI.updateRolePermissions(roleId, permissionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['role-permissions'] })
      setIsPermissionModalOpen(false)
      alert('Permissions updated successfully')
    },
    onError: () => {
      alert('Failed to update permissions')
    },
  })

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editingRole) {
        await handleUpdate(editingRole.id, formData)
      } else {
        await handleCreate(formData)
      }
      setIsModalOpen(false)
      resetForm()
    } catch (_error: unknown) {
      // Error handled by useCRUD
    }
  }

  const handleEdit = (role: Role) => {
    if (role.is_system) {
      alert('System roles cannot be edited')
      return
    }
    setEditingRole(role)
    setFormData({
      name: role.name,
      description: role.description,
      level: role.level,
    })
    setIsModalOpen(true)
  }

  const handleDeleteRole = (role: Role) => {
    if (role.is_system) {
      alert('System roles cannot be deleted')
      return
    }
    if (confirm(`Delete role "${role.name}"? This will affect all users with this role.`)) {
      handleDelete(role.id)
    }
  }

  const handleCloneRole = async (role: Role) => {
    try {
      await handleCreate({
        name: `${role.name} (Copy)`,
        description: role.description,
        level: role.level,
      })
    } catch (_error: unknown) {
      // Error handled by useCRUD
    }
  }

  const handleManagePermissions = (role: Role) => {
    setSelectedRole(role)
    setIsPermissionModalOpen(true)
  }

  const handleTogglePermission = (permissionId: number) => {
    setSelectedPermissions((prev) =>
      prev.includes(permissionId)
        ? prev.filter((id) => id !== permissionId)
        : [...prev, permissionId]
    )
  }

  const handleSavePermissions = () => {
    if (selectedRole) {
      assignPermissionsMutation.mutate({
        roleId: selectedRole.id,
        permissionIds: selectedPermissions,
      })
    }
  }

  const resetForm = () => {
    setFormData({ name: '', description: '', level: 1 })
    setEditingRole(null)
  }

  // Group permissions by resource
  const groupedPermissions: { [resource: string]: Permission[] } = {}
  permissions?.forEach((perm: Permission) => {
    if (!groupedPermissions[perm.resource]) {
      groupedPermissions[perm.resource] = []
    }
    groupedPermissions[perm.resource].push(perm)
  })

  // Calculate KPIs
  const typedRoles = roles as Role[]
  const totalRoles = typedRoles.length
  const customRoles = typedRoles.filter((r) => !r.is_system).length
  const systemRoles = typedRoles.filter((r) => r.is_system).length

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
        <p className="text-red-800">Error loading roles: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Role Management</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage user roles and their hierarchy levels. Assign permissions to roles.
          </p>
        </div>
        <Button onClick={() => { resetForm(); setIsModalOpen(true) }}>
          <Plus className="h-4 w-4 mr-2" />
          New Role
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{totalRoles}</p>
              <p className="text-sm text-gray-600">Total Roles</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{customRoles}</p>
              <p className="text-sm text-gray-600">Custom Roles</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{systemRoles}</p>
              <p className="text-sm text-gray-600">System Roles</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Roles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {typedRoles.map((role) => (
          <Card key={role.id}>
            <CardContent className="pt-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900">{role.name}</h3>
                    {role.is_system && <Badge variant="warning">System</Badge>}
                  </div>
                  <p className="text-sm text-gray-500">{role.description}</p>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Level:</span>
                  <Badge variant="default">{role.level}</Badge>
                </div>
                <div className="text-xs text-gray-400">
                  Created: {new Date(role.created_at).toLocaleDateString()}
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleManagePermissions(role)}
                  className="flex-1"
                >
                  <Shield className="h-4 w-4 mr-1" />
                  Permissions
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleEdit(role)}
                  disabled={role.is_system}
                  title="Edit"
                >
                  <Edit className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleCloneRole(role)}
                  title="Clone"
                >
                  <Copy className="h-4 w-4 text-blue-600" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleDeleteRole(role)}
                  disabled={role.is_system}
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4 text-red-600" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Create/Edit Role Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => { setIsModalOpen(false); resetForm() }}
        title={editingRole ? 'Edit Role' : 'Create New Role'}
        size="md"
      >
        <form onSubmit={handleFormSubmit} className="space-y-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role Name
            </label>
            <Input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              placeholder="e.g., Manager, Supervisor"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <Input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the role"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Hierarchy Level
            </label>
            <Input
              type="number"
              min="1"
              max="100"
              value={formData.level}
              onChange={(e) => setFormData({ ...formData, level: parseInt(e.target.value) })}
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Higher numbers = higher authority (System Admin: 100, Guest: 1)
            </p>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={() => { setIsModalOpen(false); resetForm() }}>
              Cancel
            </Button>
            <Button type="submit">
              {editingRole ? 'Update' : 'Create'} Role
            </Button>
          </div>
        </form>
      </Modal>

      {/* Manage Permissions Modal */}
      <Modal
        isOpen={isPermissionModalOpen}
        onClose={() => setIsPermissionModalOpen(false)}
        title={`Manage Permissions - ${selectedRole?.name}`}
        size="lg"
      >
        <div className="mt-4 space-y-4">
          {Object.entries(groupedPermissions).map(([resource, perms]) => (
            <div key={resource} className="border border-gray-200 rounded-md p-4">
              <h4 className="font-semibold text-gray-900 mb-3 capitalize">{resource}</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {perms.map((perm: Permission) => (
                  <label
                    key={perm.id}
                    className="flex items-center space-x-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedPermissions.includes(perm.id)}
                      onChange={() => handleTogglePermission(perm.id)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">{perm.action}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsPermissionModalOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleSavePermissions}>
              Save Permissions
            </Button>
          </div>
        </div>
      </Modal>

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-sm font-semibold text-blue-900">Role Hierarchy</h3>
        <p className="mt-2 text-sm text-blue-800">
          System Admin (100) → Organization Admin (80) → Manager (60) → Supervisor (40) → User (20) → Guest (10)
        </p>
        <p className="mt-2 text-sm text-blue-800">
          Users with higher level roles can manage users with lower level roles.
        </p>
      </div>
    </div>
  )
}
