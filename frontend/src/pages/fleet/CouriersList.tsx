import { useState, useMemo, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Eye, Filter, X } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { couriersAPI } from '@/lib/api'
import { useCRUD } from '@/hooks/useCRUD'
import { CourierForm, CourierFormData } from '@/components/forms/CourierForm'

export default function CouriersList() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCourier, setEditingCourier] = useState<any>(null)

  // Filter states
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [cityFilter, setCityFilter] = useState<string>('')
  const [nationalityFilter, setNationalityFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  // Fetch ALL couriers - use direct useQuery instead of useDataTable
  // This ensures we get all data for filter dropdowns and client-side pagination
  const {
    data: allCouriers = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(), // Uses default limit=2000 for all couriers
  })

  // Apply search filter to all data
  const filteredData = useMemo(() => {
    if (!searchTerm) return allCouriers
    const lowerSearchTerm = searchTerm.toLowerCase()
    return allCouriers.filter((item: any) =>
      Object.values(item).some((value) =>
        String(value).toLowerCase().includes(lowerSearchTerm)
      )
    )
  }, [allCouriers, searchTerm])

  // Use the reusable CRUD hook with toast notifications
  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'couriers',
    entityName: 'Courier',
    create: couriersAPI.create,
    update: couriersAPI.update,
    delete: couriersAPI.delete,
  })

  // Extract unique cities and nationalities for filter dropdowns
  // Use allCouriers (not filteredData) to ensure all options are available
  const uniqueCities = useMemo(() => {
    const cities = [...new Set(allCouriers.map((c: any) => c.city).filter(Boolean))] as string[]
    return cities.sort()
  }, [allCouriers])

  const uniqueNationalities = useMemo(() => {
    const nationalities = [...new Set(allCouriers.map((c: any) => c.nationality).filter(Boolean))] as string[]
    return nationalities.sort()
  }, [allCouriers])

  // Apply filters to data and reset page when filters change
  const finalFilteredData = useMemo(() => {
    let result = filteredData

    if (statusFilter) {
      // Case-insensitive comparison for status filter
      const filterUpper = statusFilter.toUpperCase()
      result = result.filter((c: any) => (c.status?.toUpperCase?.() || '') === filterUpper)
    }
    if (cityFilter) {
      result = result.filter((c: any) => c.city === cityFilter)
    }
    if (nationalityFilter) {
      result = result.filter((c: any) => c.nationality === nationalityFilter)
    }

    return result
  }, [filteredData, statusFilter, cityFilter, nationalityFilter])

  // Reset to page 1 when search or filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, statusFilter, cityFilter, nationalityFilter])

  // Paginate final filtered data
  const finalPaginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    const end = start + pageSize
    return finalFilteredData.slice(start, end)
  }, [finalFilteredData, currentPage, pageSize])

  const finalTotalPages = Math.ceil(finalFilteredData.length / pageSize)

  const hasActiveFilters = statusFilter || cityFilter || nationalityFilter

  const clearFilters = () => {
    setStatusFilter('')
    setCityFilter('')
    setNationalityFilter('')
    setCurrentPage(1) // Reset to first page when clearing filters
  }

  const handleOpenCreateModal = () => {
    setEditingCourier(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (courier: any) => {
    setEditingCourier(courier)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingCourier(null)
  }

  const handleFormSubmit = async (data: CourierFormData) => {
    if (editingCourier) {
      const result = await handleUpdate(editingCourier.id, data)
      if (result) {
        handleCloseModal()
      }
    } else {
      const result = await handleCreate(data)
      if (result) {
        handleCloseModal()
      }
    }
  }

  const columns = [
    { key: 'barq_id', header: 'BARQ ID', sortable: true },
    { key: 'full_name', header: 'Name', sortable: true },
    { key: 'mobile_number', header: 'Phone' },
    { key: 'city', header: 'City' },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        // Normalize status to handle both uppercase (from backend) and lowercase
        const status = row.status?.toUpperCase?.() || 'INACTIVE'
        return (
          <Badge
            variant={
              status === 'ACTIVE'
                ? 'success'
                : status === 'ON_LEAVE' || status === 'ONBOARDING'
                ? 'warning'
                : 'danger'
            }
          >
            {status.replace('_', ' ').toLowerCase().replace(/\b\w/g, (c: string) => c.toUpperCase())}
          </Badge>
        )
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => navigate(`/fleet/couriers/${row.id}`)}
            title="View Profile"
          >
            <Eye className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
            title="Edit"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete"
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
        <p className="text-red-800">Error loading couriers: {error.message}</p>
      </div>
    )
  }

  // Calculate status counts for KPI cards (using all data, not filtered)
  // Handle both uppercase (from backend) and lowercase status values
  const normalizeStatus = (status: string) => status?.toUpperCase?.() || ''
  const activeCouriers = allCouriers.filter((c: any) => normalizeStatus(c.status) === 'ACTIVE').length
  const onLeaveCouriers = allCouriers.filter((c: any) => normalizeStatus(c.status) === 'ON_LEAVE').length
  const terminatedCouriers = allCouriers.filter((c: any) => normalizeStatus(c.status) === 'TERMINATED').length

  // Status options for filter (values must match backend uppercase enum)
  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'ACTIVE', label: 'Active' },
    { value: 'ON_LEAVE', label: 'On Leave' },
    { value: 'TERMINATED', label: 'Terminated' },
    { value: 'INACTIVE', label: 'Inactive' },
    { value: 'ONBOARDING', label: 'Onboarding' },
    { value: 'SUSPENDED', label: 'Suspended' },
  ]

  // City options for filter
  const cityOptions = [
    { value: '', label: 'All Cities' },
    ...uniqueCities.map((city: string) => ({ value: city, label: city })),
  ]

  // Nationality options for filter
  const nationalityOptions = [
    { value: '', label: 'All Nationalities' },
    ...uniqueNationalities.map((nat: string) => ({ value: nat, label: nat })),
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('nav.couriers')}</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Courier
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => { clearFilters() }}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{allCouriers.length}</p>
              <p className="text-sm text-gray-600">Total Couriers</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => { clearFilters(); setStatusFilter('ACTIVE') }}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{activeCouriers}</p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => { clearFilters(); setStatusFilter('ON_LEAVE') }}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{onLeaveCouriers}</p>
              <p className="text-sm text-gray-600">On Leave</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => { clearFilters(); setStatusFilter('TERMINATED') }}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{terminatedCouriers}</p>
              <p className="text-sm text-gray-600">Terminated</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>All Couriers</CardTitle>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="h-4 w-4 mr-1" />
                Clear Filters
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {/* Search and Filters */}
          <div className="mb-4 space-y-4">
            <Input
              placeholder="Search couriers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />

            {/* Filter Row */}
            <div className="flex flex-wrap gap-3 items-center">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Filter className="h-4 w-4" />
                <span>Filters:</span>
              </div>
              <div className="w-40">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={statusOptions}
                />
              </div>
              <div className="w-40">
                <Select
                  value={cityFilter}
                  onChange={(e) => setCityFilter(e.target.value)}
                  options={cityOptions}
                />
              </div>
              <div className="w-48">
                <Select
                  value={nationalityFilter}
                  onChange={(e) => setNationalityFilter(e.target.value)}
                  options={nationalityOptions}
                />
              </div>
              {hasActiveFilters && (
                <span className="text-sm text-gray-500">
                  Showing {finalFilteredData.length} of {allCouriers.length} couriers
                </span>
              )}
            </div>
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

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingCourier ? 'Edit Courier' : 'Add New Courier'}
        size="lg"
      >
        <CourierForm
          initialData={editingCourier}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingCourier ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  )
}
