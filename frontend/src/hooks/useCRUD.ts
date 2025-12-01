import { useMutation, useQueryClient } from '@tanstack/react-query'
import { showToast } from '@/lib/toast'

export interface CRUDConfig {
  queryKey: string | string[]
  entityName?: string
}

export interface CRUDOperations<T, CreateData = Partial<T>, UpdateData = Partial<T>> {
  create?: (data: CreateData) => Promise<T>
  update?: (id: number, data: UpdateData) => Promise<T>
  delete?: (id: number) => Promise<void>
}

export interface CRUDResult<T, CreateData = Partial<T>, UpdateData = Partial<T>> {
  createMutation: ReturnType<typeof useMutation<T, Error, CreateData>>
  updateMutation: ReturnType<typeof useMutation<T, Error, { id: number; data: UpdateData }>>
  deleteMutation: ReturnType<typeof useMutation<void, Error, number>>
  isLoading: boolean
  handleCreate: (data: CreateData) => Promise<T | void>
  handleUpdate: (id: number, data: UpdateData) => Promise<T | void>
  handleDelete: (id: number) => Promise<void>
}

/**
 * Reusable hook for CRUD operations with React Query mutations
 * Includes optimistic updates, error handling, and toast notifications
 *
 * @example
 * const { handleCreate, handleUpdate, handleDelete, isLoading } = useCRUD({
 *   queryKey: 'couriers',
 *   entityName: 'Courier',
 *   create: couriersAPI.create,
 *   update: couriersAPI.update,
 *   delete: couriersAPI.delete,
 * })
 */
export function useCRUD<T, CreateData = Partial<T>, UpdateData = Partial<T>>({
  queryKey,
  entityName = 'Item',
  create,
  update,
  delete: deleteOp,
}: CRUDConfig & CRUDOperations<T, CreateData, UpdateData>): CRUDResult<T, CreateData, UpdateData> {
  const queryClient = useQueryClient()

  // Create mutation (only if create function provided)
  const createMutation = useMutation<T, Error, CreateData>({
    mutationFn: create || (() => Promise.reject(new Error('Create not implemented'))),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: Array.isArray(queryKey) ? queryKey : [queryKey]
      })
      showToast.success(`${entityName} created successfully`)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Failed to create'
      showToast.error(`Error: ${message}`)
    },
  })

  // Update mutation (only if update function provided)
  const updateMutation = useMutation<T, Error, { id: number; data: UpdateData }>({
    mutationFn: update ? ({ id, data }) => update(id, data) : () => Promise.reject(new Error('Update not implemented')),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: Array.isArray(queryKey) ? queryKey : [queryKey]
      })
      showToast.success(`${entityName} updated successfully`)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Failed to update'
      showToast.error(`Error: ${message}`)
    },
  })

  // Delete mutation (only if delete function provided)
  const deleteMutation = useMutation<void, Error, number>({
    mutationFn: deleteOp || (() => Promise.reject(new Error('Delete not implemented'))),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: Array.isArray(queryKey) ? queryKey : [queryKey]
      })
      showToast.success(`${entityName} deleted successfully`)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message || 'Failed to delete'
      showToast.error(`Error: ${message}`)
    },
  })

  // Helper functions with proper error handling
  const handleCreate = async (data: CreateData): Promise<T | void> => {
    try {
      return await createMutation.mutateAsync(data)
    } catch (error) {
      // Error already handled in onError
      return undefined
    }
  }

  const handleUpdate = async (id: number, data: UpdateData): Promise<T | void> => {
    try {
      return await updateMutation.mutateAsync({ id, data })
    } catch (error) {
      // Error already handled in onError
      return undefined
    }
  }

  const handleDelete = async (id: number): Promise<void> => {
    if (window.confirm(`Are you sure you want to delete this ${entityName.toLowerCase()}?`)) {
      try {
        await deleteMutation.mutateAsync(id)
      } catch (error) {
        // Error already handled in onError
      }
    }
  }

  const isLoading = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending

  return {
    createMutation,
    updateMutation,
    deleteMutation,
    isLoading,
    handleCreate,
    handleUpdate,
    handleDelete,
  }
}
