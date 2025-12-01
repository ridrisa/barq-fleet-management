import { describe, it, expect, vi, beforeEach, Mock } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useDataTable } from '../useDataTable'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
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
  email: string
}

const mockData: TestItem[] = [
  { id: 1, name: 'John Doe', email: 'john@example.com' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com' },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com' },
  { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com' },
]

describe('useDataTable', () => {
  let mockQueryFn: Mock

  beforeEach(() => {
    mockQueryFn = vi.fn().mockResolvedValue(mockData) as Mock
  })

  it('fetches data correctly', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.data).toEqual(mockData)
    expect(mockQueryFn).toHaveBeenCalledWith(0, 10)
  })

  it('handles pagination correctly', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 2,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.currentPage).toBe(1)
    expect(result.current.pageSize).toBe(2)
    expect(result.current.totalPages).toBe(3)
  })

  it('changes page correctly', async () => {
    const { result, rerender } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 2,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.setCurrentPage(2)
    rerender()

    await waitFor(() => {
      expect(result.current.currentPage).toBe(2)
    })

    expect(mockQueryFn).toHaveBeenCalledWith(2, 2)
  })

  it('filters data based on search term', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.setSearchTerm('john')

    await waitFor(() => {
      expect(result.current.filteredData).toHaveLength(2)
      expect(result.current.filteredData[0].name).toContain('John')
      expect(result.current.filteredData[1].name).toContain('Johnson')
    })
  })

  it('filters data case-insensitively', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.setSearchTerm('JANE')

    await waitFor(() => {
      expect(result.current.filteredData).toHaveLength(1)
      expect(result.current.filteredData[0].name).toBe('Jane Smith')
    })
  })

  it('searches across all fields', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.setSearchTerm('example.com')

    await waitFor(() => {
      expect(result.current.filteredData).toHaveLength(5)
    })
  })

  it('returns all data when search term is empty', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.setSearchTerm('john')
    result.current.setSearchTerm('')

    await waitFor(() => {
      expect(result.current.filteredData).toHaveLength(5)
    })
  })

  it('paginates filtered data', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 1,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    result.current.setSearchTerm('john')

    await waitFor(() => {
      expect(result.current.paginatedData).toHaveLength(1)
      expect(result.current.totalPages).toBe(2)
    })
  })

  it('handles initial page parameter', async () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
          initialPage: 2,
        }),
      { wrapper: createWrapper() }
    )

    expect(result.current.currentPage).toBe(2)
  })

  it('handles loading state', () => {
    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    expect(result.current.isLoading).toBe(true)
  })

  it('handles error state', async () => {
    const mockError = new Error('Failed to fetch')
    mockQueryFn.mockRejectedValueOnce(mockError)

    const { result } = renderHook(
      () =>
        useDataTable({
          queryKey: 'test-items',
          queryFn: mockQueryFn,
          pageSize: 10,
        }),
      { wrapper: createWrapper() }
    )

    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
    })
  })
})
