import { useState } from 'react'
import { Plus, Search, Edit, Trash2, Download } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { assetsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { AssetForm, AssetFormData } from '@/components/forms/AssetForm'

export default function AssetManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: assets,
    filteredData,
  } = useDataTable({
    queryKey: 'assets',
    queryFn: assetsAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete, handleUpdate, handleCreate } = useCRUD({
    queryKey: 'assets',
    entityName: 'Asset',
    create: assetsAPI.create,
    update: assetsAPI.update,
    delete: assetsAPI.delete,
  })

  const handleEdit = (asset: any) => {
    setSelectedAsset(asset)
    setIsModalOpen(true)
  }

  const handleNewAsset = () => {
    setSelectedAsset(null)
    setIsModalOpen(true)
  }

  const handleExport = () => {
    // Placeholder for export functionality
    console.log('Exporting assets...')
  }

  const handleFormSubmit = async (data: AssetFormData) => {
    if (selectedAsset) {
      await handleUpdate(selectedAsset.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setSelectedAsset(null)
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedAsset(null)
  }

  const columns = [
    {
      key: 'asset_id',
      header: 'Asset ID',
      sortable: true,
    },
    {
      key: 'asset_name',
      header: 'Asset Name',
      render: (row: any) => row.asset_name || 'N/A',
    },
    {
      key: 'asset_type',
      header: 'Type',
      render: (row: any) => (
        <Badge variant="default">
          {row.asset_type || 'general'}
        </Badge>
      ),
    },
    {
      key: 'assigned_to',
      header: 'Assigned To',
      render: (row: any) => row.assigned_to || 'Unassigned',
    },
    {
      key: 'purchase_date',
      header: 'Purchase Date',
      render: (row: any) => {
        if (!row.purchase_date) return 'N/A'
        return new Date(row.purchase_date).toLocaleDateString()
      },
    },
    {
      key: 'purchase_value',
      header: 'Value',
      render: (row: any) => row.purchase_value ? `$${row.purchase_value.toFixed(2)}` : 'N/A',
    },
    {
      key: 'depreciation',
      header: 'Depreciation',
      render: (row: any) => {
        const years = row.purchase_date
          ? (new Date().getFullYear() - new Date(row.purchase_date).getFullYear())
          : 0
        const depreciationRate = 0.2 // 20% per year
        const currentValue = row.purchase_value * Math.pow(1 - depreciationRate, years)
        return currentValue > 0 ? `$${currentValue.toFixed(2)}` : '$0.00'
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'active'
              ? 'success'
              : row.status === 'maintenance'
              ? 'warning'
              : row.status === 'retired'
              ? 'danger'
              : 'default'
          }
        >
          {row.status || 'active'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleEdit(row)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
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
        <p className="text-red-800">
          Error loading assets: {error.message}
        </p>
      </div>
    )
  }

  const totalValue = assets.reduce((sum: number, asset: any) => sum + (asset.purchase_value || 0), 0)
  const activeAssets = assets.filter((a: any) => a.status === 'active').length
  const assignedAssets = assets.filter((a: any) => a.assigned_to).length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Asset Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleNewAsset}>
            <Plus className="h-4 w-4 mr-2" />
            New Asset
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {assets.length}
              </p>
              <p className="text-sm text-gray-600">Total Assets</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {activeAssets}
              </p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {assignedAssets}
              </p>
              <p className="text-sm text-gray-600">Assigned</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                ${totalValue.toFixed(2)}
              </p>
              <p className="text-sm text-gray-600">Total Value</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-4">
            <Input
              placeholder="Search assets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={assets} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        title={selectedAsset ? 'Edit Asset' : 'New Asset'}
        size="lg"
      >
        <AssetForm
          initialData={selectedAsset}
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          mode={selectedAsset ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  )
}
