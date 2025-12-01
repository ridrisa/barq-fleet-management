import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { backupsAPI } from '@/lib/adminAPI'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'

interface Backup {
  id: number
  filename: string
  size_bytes: number
  description?: string
  created_at: string
  created_by: string
}

interface BackupSchedule {
  enabled: boolean
  frequency: string
  time: string
  last_run?: string
  next_run?: string
}

export default function Backups() {
  const [showRestoreConfirm, setShowRestoreConfirm] = useState(false)
  const [backupToRestore, setBackupToRestore] = useState<number | null>(null)
  const [newBackupDescription, setNewBackupDescription] = useState('')

  const queryClient = useQueryClient()

  const { data: backups, isLoading } = useQuery({
    queryKey: ['backups'],
    queryFn: () => backupsAPI.getAll(),
  })

  const { data: schedule } = useQuery<BackupSchedule>({
    queryKey: ['backup-schedule'],
    queryFn: () => backupsAPI.getSchedule(),
  })

  const createBackupMutation = useMutation({
    mutationFn: (description?: string) => backupsAPI.create(description),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backups'] })
      setNewBackupDescription('')
      alert('Backup created successfully')
    },
    onError: () => {
      alert('Failed to create backup')
    },
  })

  const restoreBackupMutation = useMutation({
    mutationFn: (id: number) => backupsAPI.restore(id),
    onSuccess: () => {
      setShowRestoreConfirm(false)
      setBackupToRestore(null)
      alert('Backup restored successfully. System will reload.')
      setTimeout(() => window.location.reload(), 2000)
    },
    onError: () => {
      alert('Failed to restore backup')
    },
  })

  const deleteBackupMutation = useMutation({
    mutationFn: (id: number) => backupsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backups'] })
      alert('Backup deleted successfully')
    },
    onError: () => {
      alert('Failed to delete backup')
    },
  })

  const handleDownload = async (backupId: number, filename: string) => {
    try {
      const blob = await backupsAPI.download(backupId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      alert('Failed to download backup')
    }
  }

  const handleRestore = (backupId: number) => {
    setBackupToRestore(backupId)
    setShowRestoreConfirm(true)
  }

  const confirmRestore = () => {
    if (backupToRestore) {
      restoreBackupMutation.mutate(backupToRestore)
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading backups...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-3xl font-bold text-gray-900">Backup & Restore</h1>
          <p className="mt-2 text-sm text-gray-700">
            Database backup management. Create, download, and restore backups.
          </p>
        </div>
      </div>

      {/* Create Backup Section */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Backup</h3>
          <div className="flex space-x-4">
            <Input
              type="text"
              placeholder="Backup description (optional)"
              value={newBackupDescription}
              onChange={(e) => setNewBackupDescription(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={() => createBackupMutation.mutate(newBackupDescription)}
              className="bg-primary-600 text-white hover:bg-primary-500"
              disabled={createBackupMutation.isPending}
            >
              {createBackupMutation.isPending ? 'Creating...' : 'Create Backup'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Backup Schedule */}
      {schedule && (
        <Card className="mt-6">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Automated Backup Schedule</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <p className="text-sm font-medium text-gray-700">Status</p>
                <Badge variant={schedule.enabled ? 'success' : 'error'}>
                  {schedule.enabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Frequency</p>
                <p className="text-sm text-gray-900">{schedule.frequency}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Time</p>
                <p className="text-sm text-gray-900">{schedule.time}</p>
              </div>
              {schedule.next_run && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Next Run</p>
                  <p className="text-sm text-gray-900">{new Date(schedule.next_run).toLocaleString()}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Backups List */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Backups</h3>
          <div className="space-y-3">
            {backups && backups.length > 0 ? (
              backups.map((backup: Backup) => (
                <div
                  key={backup.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-md hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900">{backup.filename}</h4>
                    {backup.description && (
                      <p className="text-sm text-gray-500 mt-1">{backup.description}</p>
                    )}
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                      <span>Size: {formatBytes(backup.size_bytes)}</span>
                      <span>Created: {new Date(backup.created_at).toLocaleString()}</span>
                      <span>By: {backup.created_by}</span>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <Button
                      onClick={() => handleDownload(backup.id, backup.filename)}
                      variant="outline"
                      size="sm"
                    >
                      Download
                    </Button>
                    <Button
                      onClick={() => handleRestore(backup.id)}
                      className="bg-yellow-600 text-white hover:bg-yellow-500"
                      size="sm"
                    >
                      Restore
                    </Button>
                    <Button
                      onClick={() => {
                        if (confirm('Delete this backup?')) {
                          deleteBackupMutation.mutate(backup.id)
                        }
                      }}
                      className="bg-red-600 text-white hover:bg-red-500"
                      size="sm"
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">No backups available</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Restore Confirmation Modal */}
      <Modal
        isOpen={showRestoreConfirm}
        onClose={() => {
          setShowRestoreConfirm(false)
          setBackupToRestore(null)
        }}
        title="Confirm Backup Restore"
      >
        <div className="mt-4">
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <h4 className="text-sm font-semibold text-red-900">CRITICAL WARNING</h4>
            <ul className="mt-2 text-sm text-red-800 list-disc list-inside space-y-1">
              <li>This will OVERWRITE ALL CURRENT DATA</li>
              <li>All changes since this backup will be PERMANENTLY LOST</li>
              <li>The system will be temporarily unavailable during restore</li>
              <li>This action CANNOT BE UNDONE</li>
            </ul>
          </div>
          <p className="text-sm text-gray-700 mb-4">
            Are you absolutely sure you want to restore this backup?
          </p>
          <div className="flex justify-end space-x-3">
            <Button
              onClick={() => {
                setShowRestoreConfirm(false)
                setBackupToRestore(null)
              }}
              variant="outline"
            >
              Cancel
            </Button>
            <Button
              onClick={confirmRestore}
              className="bg-red-600 text-white hover:bg-red-500"
            >
              Yes, Restore Backup
            </Button>
          </div>
        </div>
      </Modal>

      {/* Security Notice */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-sm font-semibold text-blue-900">Backup Best Practices</h3>
        <ul className="mt-2 text-sm text-blue-800 list-disc list-inside space-y-1">
          <li>Download and store backups in a secure off-site location</li>
          <li>Create backups before major system changes or updates</li>
          <li>Test backup restoration periodically to ensure data integrity</li>
          <li>Keep multiple backup copies from different time periods</li>
        </ul>
      </div>
    </div>
  )
}
