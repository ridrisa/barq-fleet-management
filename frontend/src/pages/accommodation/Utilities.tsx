import { useState } from 'react'
import { Plus, Search, Zap, Droplet } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { FileUpload } from '@/components/ui/FileUpload'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

const utilitiesAPI = {
  getAll: async (_skip = 0, _limit = 100) => [],
  create: async (data: any) => ({ id: Date.now(), ...data }),
  update: async (_id: number, data: any) => ({ id: Date.now(), ...data }),
  delete: async (_id: number) => {},
}

export default function Utilities() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const { isLoading, error, currentPage, pageSize, totalPages, searchTerm, setSearchTerm, setCurrentPage, paginatedData: utilities, filteredData } = useDataTable({
    queryKey: 'utilities',
    queryFn: utilitiesAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate: _handleCreate } = useCRUD({
    queryKey: 'utilities',
    entityName: 'Utility Bill',
    create: utilitiesAPI.create,
    update: utilitiesAPI.update,
    delete: utilitiesAPI.delete,
  })

  const columns = [
    { key: 'building', header: 'Building', render: (row: any) => row.building_name || 'N/A' },
    { key: 'month', header: 'Month', render: (row: any) => row.month ? new Date(row.month).toLocaleDateString('en', {month: 'long', year: 'numeric'}) : 'N/A' },
    { key: 'electricity', header: 'Electricity', render: (row: any) => `SAR ${(row.electricity || 0).toFixed(2)}` },
    { key: 'water', header: 'Water', render: (row: any) => `SAR ${(row.water || 0).toFixed(2)}` },
    { key: 'gas', header: 'Gas', render: (row: any) => `SAR ${(row.gas || 0).toFixed(2)}` },
    { key: 'total', header: 'Total Cost', render: (row: any) => <span className="font-semibold">SAR {((row.electricity || 0) + (row.water || 0) + (row.gas || 0)).toFixed(2)}</span> },
  ]

  if (isLoading) return <div className="flex items-center justify-center h-64"><Spinner /></div>
  if (error) return <div className="p-4 bg-red-50 border border-red-200 rounded-lg"><p className="text-red-800">Error: {error.message}</p></div>

  const totalMonthlyCost = 15420
  const avgPerBuilding = 3855

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Utilities</h1>
        <Button onClick={() => setIsModalOpen(true)}><Plus className="h-4 w-4 mr-2" />Add Bill</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-red-600">SAR {totalMonthlyCost.toFixed(2)}</p><p className="text-sm text-gray-600">Total Monthly Cost</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-blue-600">SAR {avgPerBuilding.toFixed(2)}</p><p className="text-sm text-gray-600">Avg Per Building</p></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Utility Bills</CardTitle></CardHeader>
        <CardContent>
          <div className="mb-4"><Input placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} leftIcon={<Search className="h-4 w-4 text-gray-400" />} /></div>
          <Table data={utilities} columns={columns} />
          <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={setCurrentPage} totalItems={filteredData.length} pageSize={pageSize} />
        </CardContent>
      </Card>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Utility Bill" size="md">
        <div className="space-y-4">
          <Input type="month" placeholder="Month" />
          <Input type="number" placeholder="Electricity (SAR)" leftIcon={<Zap className="h-4 w-4" />} />
          <Input type="number" placeholder="Water (SAR)" leftIcon={<Droplet className="h-4 w-4" />} />
          <Input type="number" placeholder="Gas (SAR)" />
          <FileUpload onFilesSelected={(files) => console.log(files)} accept={{ 'application/pdf': ['.pdf'], 'image/*': ['.png', '.jpg'] }} maxFiles={1} />
          <Button onClick={() => setIsModalOpen(false)}>Save Bill</Button>
        </div>
      </Modal>
    </div>
  )
}
