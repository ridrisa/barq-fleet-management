import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'

export interface DataTableConfig<T> {
  queryKey: string | string[]
  queryFn: (skip?: number, limit?: number) => Promise<T[]>
  pageSize?: number
  initialPage?: number
  searchFields?: string[]
}

export interface DataTableResult<T> {
  data: T[]
  isLoading: boolean
  error: Error | null
  currentPage: number
  pageSize: number
  totalPages: number
  searchTerm: string
  setSearchTerm: (term: string) => void
  setCurrentPage: (page: number) => void
  filteredData: T[]
  paginatedData: T[]
  refetch: () => void
}

/**
 * Reusable hook for managing data tables with pagination, search, and loading states
 *
 * @example
 * const { data, isLoading, error, currentPage, setCurrentPage, searchTerm, setSearchTerm, filteredData } = useDataTable({
 *   queryKey: 'couriers',
 *   queryFn: (skip, limit) => couriersAPI.getAll(skip, limit),
 *   pageSize: 10
 * })
 */
export function useDataTable<T extends Record<string, any>>({
  queryKey,
  queryFn,
  pageSize = 10,
  initialPage = 1,
}: DataTableConfig<T>): DataTableResult<T> {
  const [currentPage, setCurrentPage] = useState(initialPage)
  const [searchTerm, setSearchTerm] = useState('')

  // Fetch data with React Query
  const {
    data = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: Array.isArray(queryKey) ? [...queryKey, currentPage] : [queryKey, currentPage],
    queryFn: () => queryFn((currentPage - 1) * pageSize, pageSize),
  })

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm) return data

    const lowerSearchTerm = searchTerm.toLowerCase()
    return data.filter((item) =>
      Object.values(item).some((value) =>
        String(value).toLowerCase().includes(lowerSearchTerm)
      )
    )
  }, [data, searchTerm])

  // Paginate filtered data (client-side pagination for filtered results)
  const paginatedData = useMemo(() => {
    if (searchTerm) {
      const start = (currentPage - 1) * pageSize
      const end = start + pageSize
      return filteredData.slice(start, end)
    }
    return filteredData
  }, [filteredData, currentPage, pageSize, searchTerm])

  const totalPages = Math.ceil(filteredData.length / pageSize)

  return {
    data,
    isLoading,
    error: error as Error | null,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
    paginatedData,
    refetch,
  }
}
