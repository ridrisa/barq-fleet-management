import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { FileUpload } from '@/components/ui/FileUpload'

interface Contract {
  id: number
  building_name: string
  contract_type: 'lease' | 'insurance' | 'maintenance' | 'utility'
  vendor_name: string
  start_date: string
  end_date: string
  amount: number
  status: 'active' | 'expiring' | 'expired' | 'renewed'
  documents: {
    name: string
    url: string
    version: number
    uploaded_date: string
  }[]
}

export default function Contracts() {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null)
  const [documents, setDocuments] = useState<File[]>([])

  const [formData, setFormData] = useState({
    building_id: 0,
    contract_type: 'lease' as Contract['contract_type'],
    vendor_name: '',
    start_date: '',
    end_date: '',
    amount: 0,
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      // Mock data
      const mockContracts: Contract[] = [
        {
          id: 1,
          building_name: 'Downtown Residence',
          contract_type: 'lease',
          vendor_name: 'Property Owner LLC',
          start_date: '2024-01-01',
          end_date: '2024-12-31',
          amount: 500000,
          status: 'active',
          documents: [
            {
              name: 'Lease Agreement 2024.pdf',
              url: '#',
              version: 1,
              uploaded_date: '2024-01-01',
            },
          ],
        },
        {
          id: 2,
          building_name: 'Downtown Residence',
          contract_type: 'insurance',
          vendor_name: 'Insurance Co.',
          start_date: '2024-02-01',
          end_date: '2024-06-30',
          amount: 50000,
          status: 'expiring',
          documents: [
            {
              name: 'Insurance Policy.pdf',
              url: '#',
              version: 1,
              uploaded_date: '2024-02-01',
            },
            {
              name: 'Insurance Policy.pdf',
              url: '#',
              version: 2,
              uploaded_date: '2024-02-15',
            },
          ],
        },
        {
          id: 3,
          building_name: 'Marina Tower',
          contract_type: 'maintenance',
          vendor_name: 'Facility Management Inc.',
          start_date: '2023-01-01',
          end_date: '2023-12-31',
          amount: 100000,
          status: 'expired',
          documents: [
            {
              name: 'Maintenance Contract.pdf',
              url: '#',
              version: 1,
              uploaded_date: '2023-01-01',
            },
          ],
        },
      ]
      setContracts(mockContracts)
    } catch (error) {
      console.error('Failed to fetch contracts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      console.log('Creating contract:', formData)
      // API call would go here
      fetchData()
      handleCloseModal()
    } catch (error) {
      console.error('Failed to create contract:', error)
    }
  }

  const handleUploadDocument = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      console.log('Uploading document for contract:', selectedContract, documents)
      // API call would go here
      fetchData()
      handleCloseUploadModal()
    } catch (error) {
      console.error('Failed to upload document:', error)
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setFormData({
      building_id: 0,
      contract_type: 'lease',
      vendor_name: '',
      start_date: '',
      end_date: '',
      amount: 0,
    })
  }

  const handleCloseUploadModal = () => {
    setShowUploadModal(false)
    setSelectedContract(null)
    setDocuments([])
  }

  const getStatusColor = (status: Contract['status']) => {
    const colors = {
      active: 'success',
      expiring: 'warning',
      expired: 'error',
      renewed: 'primary',
    }
    return colors[status] as 'success' | 'warning' | 'error' | 'primary'
  }

  const getDaysUntilExpiry = (endDate: string) => {
    const today = new Date()
    const expiry = new Date(endDate)
    const diffTime = expiry.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Contracts</h1>
        <Button onClick={() => setShowModal(true)}>New Contract</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{contracts.length}</div>
            <div className="text-sm text-gray-600">Total Contracts</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {contracts.filter((c) => c.status === 'active').length}
            </div>
            <div className="text-sm text-gray-600">Active</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-yellow-600">
              {contracts.filter((c) => c.status === 'expiring').length}
            </div>
            <div className="text-sm text-gray-600">Expiring Soon</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">
              {contracts.filter((c) => c.status === 'expired').length}
            </div>
            <div className="text-sm text-gray-600">Expired</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="space-y-4">
              {contracts.map((contract) => {
                const daysUntilExpiry = getDaysUntilExpiry(contract.end_date)
                return (
                  <Card key={contract.id} className="border-l-4 border-purple-500">
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg">
                            {contract.building_name} - {contract.contract_type}
                          </h3>
                          <p className="text-sm text-gray-600">{contract.vendor_name}</p>
                        </div>
                        <Badge variant={getStatusColor(contract.status)}>
                          {contract.status}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        <div>
                          <p className="text-xs text-gray-500">Start Date</p>
                          <p className="font-medium">
                            {new Date(contract.start_date).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">End Date</p>
                          <p className="font-medium">
                            {new Date(contract.end_date).toLocaleDateString()}
                            {daysUntilExpiry > 0 && daysUntilExpiry <= 30 && (
                              <span className="ml-2 text-xs text-red-600">
                                ({daysUntilExpiry} days left)
                              </span>
                            )}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Amount</p>
                          <p className="font-medium">
                            SAR {contract.amount.toLocaleString()}
                          </p>
                        </div>
                      </div>

                      <div className="mb-3">
                        <p className="text-xs text-gray-500 mb-2">Documents:</p>
                        <div className="space-y-1">
                          {contract.documents.map((doc, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-2 bg-gray-50 rounded"
                            >
                              <div className="flex items-center">
                                <svg
                                  className="w-4 h-4 mr-2 text-gray-400"
                                  fill="none"
                                  stroke="currentColor"
                                  viewBox="0 0 24 24"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                  />
                                </svg>
                                <span className="text-sm">{doc.name}</span>
                                <span className="ml-2 text-xs text-gray-500">
                                  v{doc.version}
                                </span>
                              </div>
                              <a
                                href={doc.url}
                                className="text-blue-600 hover:underline text-xs"
                              >
                                Download
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedContract(contract)
                            setShowUploadModal(true)
                          }}
                        >
                          Upload New Version
                        </Button>
                        <Button variant="outline" size="sm">
                          Renew Contract
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title="New Contract"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Building</label>
            <Select
              required
              value={formData.building_id}
              onChange={(e) =>
                setFormData({ ...formData, building_id: parseInt(e.target.value) })
              }
            >
              <option value="">Select Building</option>
              <option value="1">Downtown Residence</option>
              <option value="2">Marina Tower</option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Contract Type</label>
            <Select
              value={formData.contract_type}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  contract_type: e.target.value as Contract['contract_type'],
                })
              }
            >
              <option value="lease">Lease Agreement</option>
              <option value="insurance">Insurance Policy</option>
              <option value="maintenance">Maintenance Contract</option>
              <option value="utility">Utility Contract</option>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Vendor Name</label>
            <Input
              required
              value={formData.vendor_name}
              onChange={(e) =>
                setFormData({ ...formData, vendor_name: e.target.value })
              }
              placeholder="Property Owner LLC"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Date</label>
              <input
                type="date"
                required
                value={formData.start_date}
                onChange={(e) =>
                  setFormData({ ...formData, start_date: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date</label>
              <input
                type="date"
                required
                value={formData.end_date}
                onChange={(e) =>
                  setFormData({ ...formData, end_date: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Amount (SAR)</label>
            <Input
              type="number"
              required
              value={formData.amount}
              onChange={(e) =>
                setFormData({ ...formData, amount: parseFloat(e.target.value) })
              }
              placeholder="500000"
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              Create Contract
            </Button>
            <Button type="button" variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={showUploadModal}
        onClose={handleCloseUploadModal}
        title="Upload New Document Version"
      >
        <form onSubmit={handleUploadDocument} className="space-y-4">
          {selectedContract && (
            <div className="p-3 bg-gray-50 rounded mb-4">
              <p className="font-medium">
                {selectedContract.building_name} - {selectedContract.contract_type}
              </p>
              <p className="text-sm text-gray-600">
                Current version: v{selectedContract.documents[selectedContract.documents.length - 1].version}
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Upload Document</label>
            <FileUpload
              accept={{ 'application/pdf': ['.pdf'], 'application/msword': ['.doc', '.docx'] }}
              maxFiles={1}
              maxSize={10 * 1024 * 1024}
              onFilesSelected={setDocuments}
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              Upload
            </Button>
            <Button type="button" variant="outline" onClick={handleCloseUploadModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
