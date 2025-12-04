import { api } from './api'

// ============================================
// ADMIN APIs - Role-Based Access Control (RBAC)
// ============================================

// Admin APIs - Role Management
export const rolesAPI = {
  getAll: async () => {
    const response = await api.get('/admin/roles')
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/admin/roles/${id}`)
    return response.data
  },
  create: async (data: { name: string; description?: string; level: number }) => {
    const response = await api.post('/admin/roles', data)
    return response.data
  },
  update: async (id: number, data: { name?: string; description?: string; level?: number }) => {
    const response = await api.put(`/admin/roles/${id}`, data)
    return response.data
  },
  delete: async (id: number) => {
    const response = await api.delete(`/admin/roles/${id}`)
    return response.data
  },
}

// Admin APIs - Permission Management
export const permissionsAPI = {
  getAll: async () => {
    const response = await api.get('/admin/permissions')
    return response.data
  },
  getByRole: async (roleId: number) => {
    const response = await api.get(`/admin/roles/${roleId}/permissions`)
    return response.data
  },
  assignToRole: async (roleId: number, permissionIds: number[]) => {
    const response = await api.post(`/admin/roles/${roleId}/permissions`, { permission_ids: permissionIds })
    return response.data
  },
  removeFromRole: async (roleId: number, permissionId: number) => {
    const response = await api.delete(`/admin/roles/${roleId}/permissions/${permissionId}`)
    return response.data
  },
  updateRolePermissions: async (roleId: number, permissionIds: number[]) => {
    const response = await api.put(`/admin/roles/${roleId}/permissions`, { permission_ids: permissionIds })
    return response.data
  },
}

// Admin APIs - Audit Logs
export const auditLogsAPI = {
  getAll: async (params?: { skip?: number; limit?: number; user_id?: number; action?: string; start_date?: string; end_date?: string }) => {
    const response = await api.get('/admin/audit-logs', { params })
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/admin/audit-logs/${id}`)
    return response.data
  },
  exportToExcel: async (params?: { user_id?: number; action?: string; start_date?: string; end_date?: string }) => {
    const response = await api.get('/admin/audit-logs/export', {
      params,
      responseType: 'blob'
    })
    return response.data
  },
}

// Admin APIs - System Settings
export const settingsAPI = {
  getAll: async () => {
    const response = await api.get('/admin/settings')
    return response.data
  },
  getByKey: async (key: string) => {
    const response = await api.get(`/admin/settings/${key}`)
    return response.data
  },
  update: async (key: string, value: any) => {
    const response = await api.put(`/admin/settings/${key}`, { value })
    return response.data
  },
  updateBulk: async (settings: Record<string, any>) => {
    const response = await api.put('/admin/settings/bulk', settings)
    return response.data
  },
}

// Admin APIs - Backup & Restore
export const backupsAPI = {
  getAll: async () => {
    const response = await api.get('/admin/backups')
    return response.data
  },
  create: async (description?: string) => {
    const response = await api.post('/admin/backups', { description })
    return response.data
  },
  download: async (id: number) => {
    const response = await api.get(`/admin/backups/${id}/download`, {
      responseType: 'blob'
    })
    return response.data
  },
  restore: async (id: number) => {
    const response = await api.post(`/admin/backups/${id}/restore`)
    return response.data
  },
  delete: async (id: number) => {
    const response = await api.delete(`/admin/backups/${id}`)
    return response.data
  },
  getSchedule: async () => {
    const response = await api.get('/admin/backups/schedule')
    return response.data
  },
  updateSchedule: async (data: { enabled: boolean; frequency: string; time: string }) => {
    const response = await api.put('/admin/backups/schedule', data)
    return response.data
  },
}

// Admin APIs - Email Templates
export const emailTemplatesAPI = {
  getAll: async () => {
    const response = await api.get('/admin/email-templates')
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/admin/email-templates/${id}`)
    return response.data
  },
  create: async (data: { name: string; subject: string; body: string; variables?: string[] }) => {
    const response = await api.post('/admin/email-templates', data)
    return response.data
  },
  update: async (id: number, data: { name?: string; subject?: string; body?: string; variables?: string[] }) => {
    const response = await api.put(`/admin/email-templates/${id}`, data)
    return response.data
  },
  delete: async (id: number) => {
    const response = await api.delete(`/admin/email-templates/${id}`)
    return response.data
  },
  sendTest: async (id: number, email: string) => {
    const response = await api.post(`/admin/email-templates/${id}/test`, { email })
    return response.data
  },
}

// Admin APIs - API Keys
export const apiKeysAPI = {
  getAll: async () => {
    const response = await api.get('/admin/api-keys')
    return response.data
  },
  create: async (data: { name: string; description?: string; rate_limit?: number }) => {
    const response = await api.post('/admin/api-keys', data)
    return response.data
  },
  revoke: async (id: number) => {
    const response = await api.delete(`/admin/api-keys/${id}`)
    return response.data
  },
  getUsage: async (id: number, days: number = 30) => {
    const response = await api.get(`/admin/api-keys/${id}/usage`, { params: { days } })
    return response.data
  },
  updateRateLimit: async (id: number, rateLimit: number) => {
    const response = await api.put(`/admin/api-keys/${id}/rate-limit`, { rate_limit: rateLimit })
    return response.data
  },
}

// Admin APIs - Enhanced User Management
export const adminUsersAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/admin/users', { params: { skip, limit } })
    return response.data
  },
  getById: async (id: number) => {
    const response = await api.get(`/admin/users/${id}`)
    return response.data
  },
  create: async (data: { email: string; password?: string; full_name?: string; role?: string; is_active?: boolean; department?: string; phone?: string }) => {
    const response = await api.post('/admin/users', data)
    return response.data
  },
  update: async (id: number, data: { email?: string; full_name?: string; role?: string; is_active?: boolean; department?: string; phone?: string }) => {
    const response = await api.patch(`/admin/users/${id}`, data)
    return response.data
  },
  delete: async (id: number) => {
    const response = await api.delete(`/admin/users/${id}`)
    return response.data
  },
  bulkActivate: async (userIds: number[]) => {
    const response = await api.post('/admin/users/bulk-activate', { user_ids: userIds })
    return response.data
  },
  bulkDeactivate: async (userIds: number[]) => {
    const response = await api.post('/admin/users/bulk-deactivate', { user_ids: userIds })
    return response.data
  },
  getActivityLogs: async (userId: number, limit: number = 50) => {
    const response = await api.get(`/admin/users/${userId}/activity-logs`, { params: { limit } })
    return response.data
  },
  resetPassword: async (userId: number) => {
    const response = await api.post(`/admin/users/${userId}/reset-password`)
    return response.data
  },
  updateRole: async (userId: number, roleId: number) => {
    const response = await api.put(`/admin/users/${userId}/role`, { role_id: roleId })
    return response.data
  },
}
