import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { rolesAPI, permissionsAPI } from '@/lib/adminAPI'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

interface Permission {
  id: number
  name: string
  resource: string
  action: string
  description: string
}

interface Role {
  id: number
  name: string
  description: string
  level: number
}

interface PermissionMatrix {
  [roleId: number]: {
    [permissionId: number]: boolean
  }
}

export default function Permissions() {
  const [permissionMatrix, setPermissionMatrix] = useState<PermissionMatrix>({})
  const [hasChanges, setHasChanges] = useState(false)

  const queryClient = useQueryClient()

  const { data: roles, isLoading: loadingRoles } = useQuery({
    queryKey: ['roles'],
    queryFn: () => rolesAPI.getAll(),
  })

  const { data: permissions, isLoading: loadingPermissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionsAPI.getAll(),
  })

  const updatePermissionsMutation = useMutation({
    mutationFn: async () => {
      const updates = Object.entries(permissionMatrix).map(([roleId, perms]) => {
        const permissionIds = Object.entries(perms)
          .filter(([_, enabled]) => enabled)
          .map(([permId]) => parseInt(permId))
        return permissionsAPI.updateRolePermissions(parseInt(roleId), permissionIds)
      })
      return Promise.all(updates)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] })
      setHasChanges(false)
      alert('Permissions updated successfully')
    },
    onError: () => {
      alert('Failed to update permissions')
    },
  })

  useEffect(() => {
    if (roles && permissions) {
      const matrix: PermissionMatrix = {}
      roles.forEach((role: Role) => {
        matrix[role.id] = {}
        permissions.forEach((perm: Permission) => {
          matrix[role.id][perm.id] = false
        })
      })
      setPermissionMatrix(matrix)
    }
  }, [roles, permissions])

  const togglePermission = (roleId: number, permissionId: number) => {
    setPermissionMatrix(prev => ({
      ...prev,
      [roleId]: {
        ...prev[roleId],
        [permissionId]: !prev[roleId]?.[permissionId]
      }
    }))
    setHasChanges(true)
  }

  const toggleAllForRole = (roleId: number, enabled: boolean) => {
    setPermissionMatrix(prev => {
      const newMatrix = { ...prev }
      Object.keys(newMatrix[roleId] || {}).forEach(permId => {
        newMatrix[roleId][parseInt(permId)] = enabled
      })
      return newMatrix
    })
    setHasChanges(true)
  }

  const handleSave = () => {
    if (confirm('Save permission changes? This will affect all users with these roles.')) {
      updatePermissionsMutation.mutate()
    }
  }

  if (loadingRoles || loadingPermissions) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading permissions...</div>
      </div>
    )
  }

  const groupedPermissions: { [resource: string]: Permission[] } = {}
  permissions?.forEach((perm: Permission) => {
    if (!groupedPermissions[perm.resource]) {
      groupedPermissions[perm.resource] = []
    }
    groupedPermissions[perm.resource].push(perm)
  })

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Permission Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Fine-grained permission matrix. Configure which roles can perform which actions on each resource.
          </p>
        </div>
        {hasChanges && (
          <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none space-x-2">
            <Button
              onClick={() => {
                setHasChanges(false)
                window.location.reload()
              }}
              variant="outline"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              className="bg-green-600 text-white hover:bg-green-500"
            >
              Save Changes
            </Button>
          </div>
        )}
      </div>

      {hasChanges && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <p className="text-sm text-yellow-800">
            You have unsaved changes. Click "Save Changes" to apply them.
          </p>
        </div>
      )}

      <Card>
        <CardContent className="pt-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="sticky left-0 z-10 bg-gray-50 py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">
                    Resource / Permission
                  </th>
                  {roles?.map((role: Role) => (
                    <th
                      key={role.id}
                      className="px-3 py-3.5 text-center text-sm font-semibold text-gray-900"
                    >
                      <div className="flex flex-col items-center">
                        <span>{role.name}</span>
                        <span className="text-xs text-gray-500 mt-1">Level: {role.level}</span>
                        <button
                          onClick={() => toggleAllForRole(role.id, true)}
                          className="text-xs text-green-600 hover:text-green-900 mt-1"
                        >
                          All
                        </button>
                        <button
                          onClick={() => toggleAllForRole(role.id, false)}
                          className="text-xs text-red-600 hover:text-red-900"
                        >
                          None
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {Object.entries(groupedPermissions).map(([resource, perms]) => (
                  <>
                    <tr key={`resource-${resource}`} className="bg-gray-100">
                      <td
                        colSpan={100}
                        className="sticky left-0 z-10 bg-gray-100 py-2 pl-4 pr-3 text-sm font-semibold text-gray-900"
                      >
                        {resource.toUpperCase()}
                      </td>
                    </tr>
                    {perms.map((perm: Permission) => (
                      <tr key={perm.id}>
                        <td className="sticky left-0 z-10 bg-white py-4 pl-8 pr-3 text-sm text-gray-900">
                          <div>
                            <span className="font-medium">{perm.action}</span>
                            <p className="text-xs text-gray-500 mt-1">{perm.description}</p>
                          </div>
                        </td>
                        {roles?.map((role: Role) => (
                          <td key={`${role.id}-${perm.id}`} className="px-3 py-4 text-center">
                            <input
                              type="checkbox"
                              checked={permissionMatrix[role.id]?.[perm.id] || false}
                              onChange={() => togglePermission(role.id, perm.id)}
                              className="h-5 w-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-sm font-semibold text-blue-900">Permission Legend</h3>
        <ul className="mt-2 text-sm text-blue-800 space-y-1">
          <li><strong>create:</strong> Can create new records</li>
          <li><strong>read:</strong> Can view records</li>
          <li><strong>update:</strong> Can edit existing records</li>
          <li><strong>delete:</strong> Can remove records</li>
          <li><strong>approve:</strong> Can approve workflows/requests</li>
          <li><strong>export:</strong> Can export data to Excel/CSV</li>
        </ul>
      </div>
    </div>
  )
}
