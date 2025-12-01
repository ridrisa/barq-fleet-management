import { describe, it, expect, vi, beforeEach, Mock } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useCRUD } from '../useCRUD'
import * as toastLib from '@/lib/toast'

// Mock toast
vi.mock('@/lib/toast', () => ({
  showToast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock window.confirm
global.confirm = vi.fn(() => true)

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

interface TestItem {
  id: number
  name: string
}

describe('useCRUD', () => {
  let mockCreate: Mock
  let mockUpdate: Mock
  let mockDelete: Mock

  beforeEach(() => {
    mockCreate = vi.fn() as Mock
    mockUpdate = vi.fn() as Mock
    mockDelete = vi.fn() as Mock
    vi.clearAllMocks()
  })

  it('creates item successfully', async () => {
    const newItem = { id: 1, name: 'Test Item' }
    mockCreate.mockResolvedValue(newItem)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleCreate({ name: 'Test Item' })

    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalledWith({ name: 'Test Item' })
      expect(toastLib.showToast.success).toHaveBeenCalledWith('Test Item created successfully')
    })
  })

  it('updates item successfully', async () => {
    const updatedItem = { id: 1, name: 'Updated Item' }
    mockUpdate.mockResolvedValue(updatedItem)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleUpdate(1, { name: 'Updated Item' })

    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, { name: 'Updated Item' })
      expect(toastLib.showToast.success).toHaveBeenCalledWith('Test Item updated successfully')
    })
  })

  it('deletes item successfully', async () => {
    mockDelete.mockResolvedValue(undefined)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleDelete(1)

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith(1)
      expect(toastLib.showToast.success).toHaveBeenCalledWith('Test Item deleted successfully')
    })
  })

  it('shows confirmation dialog before delete', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm')
    mockDelete.mockResolvedValue(undefined)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleDelete(1)

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this test item?')
  })

  it('does not delete when confirmation is cancelled', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleDelete(1)

    expect(mockDelete).not.toHaveBeenCalled()
  })

  it('handles create error', async () => {
    const error = new Error('Create failed')
    mockCreate.mockRejectedValue(error)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleCreate({ name: 'Test Item' })

    await waitFor(() => {
      expect(toastLib.showToast.error).toHaveBeenCalledWith('Error: Create failed')
    })
  })

  it('handles update error', async () => {
    const error = new Error('Update failed')
    mockUpdate.mockRejectedValue(error)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleUpdate(1, { name: 'Updated Item' })

    await waitFor(() => {
      expect(toastLib.showToast.error).toHaveBeenCalledWith('Error: Update failed')
    })
  })

  it('handles delete error', async () => {
    const error = new Error('Delete failed')
    mockDelete.mockRejectedValue(error)

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleDelete(1)

    await waitFor(() => {
      expect(toastLib.showToast.error).toHaveBeenCalledWith('Error: Delete failed')
    })
  })

  it('sets isLoading correctly during operations', async () => {
    mockCreate.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ id: 1, name: 'Test' }), 100))
    )

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          entityName: 'Test Item',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    expect(result.current.isLoading).toBe(false)

    result.current.handleCreate({ name: 'Test Item' })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(true)
    })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })
  })

  it('uses default entity name when not provided', async () => {
    mockCreate.mockResolvedValue({ id: 1, name: 'Test' })

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper: createWrapper() }
    )

    await result.current.handleCreate({ name: 'Test' })

    await waitFor(() => {
      expect(toastLib.showToast.success).toHaveBeenCalledWith('Item created successfully')
    })
  })

  it('invalidates query cache after create', async () => {
    mockCreate.mockResolvedValue({ id: 1, name: 'Test' })

    const queryClient = new QueryClient()
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    )

    const { result } = renderHook(
      () =>
        useCRUD<TestItem>({
          queryKey: 'test-items',
          create: mockCreate,
          update: mockUpdate,
          delete: mockDelete,
        }),
      { wrapper }
    )

    await result.current.handleCreate({ name: 'Test' })

    await waitFor(() => {
      expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['test-items'] })
    })
  })
})
