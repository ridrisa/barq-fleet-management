import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { FileUpload } from '@/components/ui/FileUpload'

interface InventoryItem {
  id: number
  building_name: string
  room_number: string
  item_name: string
  category: 'furniture' | 'appliance' | 'electronics' | 'fixture' | 'other'
  quantity: number
  condition: 'excellent' | 'good' | 'fair' | 'poor' | 'damaged'
  purchase_date: string
  last_inspection: string
  photos: string[]
  notes: string
}

export default function Inventory() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [photos, setPhotos] = useState<File[]>([])

  const [formData, setFormData] = useState({
    building_id: 0,
    room_number: '',
    item_name: '',
    category: 'furniture' as InventoryItem['category'],
    quantity: 1,
    condition: 'good' as InventoryItem['condition'],
    purchase_date: '',
    notes: '',
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      // Mock data
      const mockItems: InventoryItem[] = [
        {
          id: 1,
          building_name: 'Downtown Residence',
          room_number: '101',
          item_name: 'Bed Frame (Double)',
          category: 'furniture',
          quantity: 2,
          condition: 'good',
          purchase_date: '2024-01-15',
          last_inspection: '2024-03-01',
          photos: ['/placeholder-bed.jpg'],
          notes: 'Standard double bed frames',
        },
        {
          id: 2,
          building_name: 'Downtown Residence',
          room_number: '101',
          item_name: 'Air Conditioner',
          category: 'appliance',
          quantity: 1,
          condition: 'fair',
          purchase_date: '2023-06-10',
          last_inspection: '2024-03-01',
          photos: [],
          notes: 'Requires servicing soon',
        },
        {
          id: 3,
          building_name: 'Marina Tower',
          room_number: '301',
          item_name: 'Wardrobe',
          category: 'furniture',
          quantity: 1,
          condition: 'excellent',
          purchase_date: '2024-02-01',
          last_inspection: '2024-02-15',
          photos: ['/placeholder-wardrobe.jpg'],
          notes: 'New purchase',
        },
        {
          id: 4,
          building_name: 'Downtown Residence',
          room_number: '102',
          item_name: 'Refrigerator',
          category: 'appliance',
          quantity: 1,
          condition: 'damaged',
          purchase_date: '2023-01-15',
          last_inspection: '2024-03-05',
          photos: [],
          notes: 'Needs replacement',
        },
      ]
      setItems(mockItems)
    } catch (error) {
      console.error('Failed to fetch inventory:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      console.log('Saving inventory item:', formData, photos)
      // API call would go here
      fetchData()
      handleCloseModal()
    } catch (error) {
      console.error('Failed to save item:', error)
    }
  }

  const handleEdit = (item: InventoryItem) => {
    setEditingItem(item)
    setFormData({
      building_id: 1, // would be item.building_id
      room_number: item.room_number,
      item_name: item.item_name,
      category: item.category,
      quantity: item.quantity,
      condition: item.condition,
      purchase_date: item.purchase_date,
      notes: item.notes,
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        console.log('Deleting item:', id)
        fetchData()
      } catch (error) {
        console.error('Failed to delete item:', error)
      }
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingItem(null)
    setFormData({
      building_id: 0,
      room_number: '',
      item_name: '',
      category: 'furniture',
      quantity: 1,
      condition: 'good',
      purchase_date: '',
      notes: '',
    })
    setPhotos([])
  }

  const getConditionColor = (condition: InventoryItem['condition']) => {
    const colors = {
      excellent: 'success',
      good: 'primary',
      fair: 'warning',
      poor: 'secondary',
      damaged: 'error',
    }
    return colors[condition] as 'success' | 'primary' | 'warning' | 'secondary' | 'error'
  }

  const filteredItems = items.filter((item) => {
    const matchesSearch =
      item.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.room_number.includes(searchTerm) ||
      item.building_name.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesCategory = !selectedCategory || item.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  const stats = {
    total: items.length,
    excellent: items.filter((i) => i.condition === 'excellent').length,
    needsAttention: items.filter((i) =>
      ['poor', 'damaged'].includes(i.condition)
    ).length,
    furniture: items.filter((i) => i.category === 'furniture').length,
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Room Inventory</h1>
        <Button onClick={() => setShowModal(true)}>Add Item</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Items</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {stats.excellent}
            </div>
            <div className="text-sm text-gray-600">Excellent Condition</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">
              {stats.needsAttention}
            </div>
            <div className="text-sm text-gray-600">Needs Attention</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">
              {stats.furniture}
            </div>
            <div className="text-sm text-gray-600">Furniture Items</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4 mb-6">
            <Input
              placeholder="Search items..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1"
            />
            <Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-48"
            >
              <option value="">All Categories</option>
              <option value="furniture">Furniture</option>
              <option value="appliance">Appliance</option>
              <option value="electronics">Electronics</option>
              <option value="fixture">Fixture</option>
              <option value="other">Other</option>
            </Select>
          </div>

          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Item</th>
                    <th className="text-left p-3">Location</th>
                    <th className="text-left p-3">Category</th>
                    <th className="text-left p-3">Quantity</th>
                    <th className="text-left p-3">Condition</th>
                    <th className="text-left p-3">Last Inspection</th>
                    <th className="text-left p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredItems.map((item) => (
                    <tr key={item.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        <div className="flex items-center">
                          {item.photos.length > 0 ? (
                            <div className="w-10 h-10 bg-gray-200 rounded mr-3 flex items-center justify-center">
                              <svg
                                className="w-6 h-6 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                                />
                              </svg>
                            </div>
                          ) : null}
                          <div>
                            <div className="font-medium">{item.item_name}</div>
                            {item.notes && (
                              <div className="text-xs text-gray-500">
                                {item.notes}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="p-3">
                        {item.building_name}
                        <br />
                        <span className="text-sm text-gray-600">
                          Room {item.room_number}
                        </span>
                      </td>
                      <td className="p-3 capitalize">{item.category}</td>
                      <td className="p-3">{item.quantity}</td>
                      <td className="p-3">
                        <Badge variant={getConditionColor(item.condition)}>
                          {item.condition}
                        </Badge>
                      </td>
                      <td className="p-3">
                        {new Date(item.last_inspection).toLocaleDateString()}
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(item)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(item.id)}
                          >
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title={editingItem ? 'Edit Inventory Item' : 'Add Inventory Item'}
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
            <label className="block text-sm font-medium mb-1">Room Number</label>
            <Input
              required
              value={formData.room_number}
              onChange={(e) =>
                setFormData({ ...formData, room_number: e.target.value })
              }
              placeholder="101"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Item Name</label>
            <Input
              required
              value={formData.item_name}
              onChange={(e) =>
                setFormData({ ...formData, item_name: e.target.value })
              }
              placeholder="Bed Frame (Double)"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Category</label>
              <Select
                value={formData.category}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    category: e.target.value as InventoryItem['category'],
                  })
                }
              >
                <option value="furniture">Furniture</option>
                <option value="appliance">Appliance</option>
                <option value="electronics">Electronics</option>
                <option value="fixture">Fixture</option>
                <option value="other">Other</option>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Quantity</label>
              <Input
                type="number"
                required
                value={formData.quantity}
                onChange={(e) =>
                  setFormData({ ...formData, quantity: parseInt(e.target.value) })
                }
                placeholder="1"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Condition</label>
              <Select
                value={formData.condition}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    condition: e.target.value as InventoryItem['condition'],
                  })
                }
              >
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
                <option value="damaged">Damaged</option>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Purchase Date
              </label>
              <input
                type="date"
                required
                value={formData.purchase_date}
                onChange={(e) =>
                  setFormData({ ...formData, purchase_date: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows={2}
              placeholder="Additional notes..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Upload Photos</label>
            <FileUpload
              accept={{ 'image/*': ['.png', '.jpg', '.jpeg'] }}
              maxFiles={5}
              maxSize={5 * 1024 * 1024}
              onFilesSelected={setPhotos}
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              {editingItem ? 'Update' : 'Add'} Item
            </Button>
            <Button type="button" variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
