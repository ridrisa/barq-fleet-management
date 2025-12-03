import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'

interface BedAssignment {
  id: number
  room_id: number
  room_number: string
  bed_number: string
  courier_id: number | null
  courier_name: string | null
  assigned_date: string | null
  status: 'vacant' | 'occupied' | 'reserved'
}

interface Courier {
  id: number
  name: string
}

interface TransferHistory {
  id: number
  courier_name: string
  from_bed: string
  to_bed: string
  transfer_date: string
  reason: string
}

export default function BedAssignment() {
  const [beds, setBeds] = useState<BedAssignment[]>([])
  const [couriers, setCouriers] = useState<Courier[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedBed, setSelectedBed] = useState<BedAssignment | null>(null)
  const [selectedRoom, setSelectedRoom] = useState<number | null>(null)
  const [transferHistory, setTransferHistory] = useState<TransferHistory[]>([])

  const [formData, setFormData] = useState({
    courier_id: 0,
    assigned_date: new Date().toISOString().split('T')[0],
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      // Mock data
      const mockCouriers: Courier[] = [
        { id: 1, name: 'Ahmed Ali' },
        { id: 2, name: 'Mohammed Hassan' },
        { id: 3, name: 'Fatima Ahmed' },
      ]
      setCouriers(mockCouriers)

      const mockBeds: BedAssignment[] = [
        {
          id: 1,
          room_id: 1,
          room_number: '101',
          bed_number: 'A',
          courier_id: 1,
          courier_name: 'Ahmed Ali',
          assigned_date: '2024-01-15',
          status: 'occupied',
        },
        {
          id: 2,
          room_id: 1,
          room_number: '101',
          bed_number: 'B',
          courier_id: 2,
          courier_name: 'Mohammed Hassan',
          assigned_date: '2024-01-15',
          status: 'occupied',
        },
        {
          id: 3,
          room_id: 2,
          room_number: '102',
          bed_number: 'A',
          courier_id: null,
          courier_name: null,
          assigned_date: null,
          status: 'vacant',
        },
        {
          id: 4,
          room_id: 2,
          room_number: '102',
          bed_number: 'B',
          courier_id: 3,
          courier_name: 'Fatima Ahmed',
          assigned_date: '2024-02-01',
          status: 'occupied',
        },
      ]
      setBeds(mockBeds)

      const mockTransfers: TransferHistory[] = [
        {
          id: 1,
          courier_name: 'Ahmed Ali',
          from_bed: 'Room 102-A',
          to_bed: 'Room 101-A',
          transfer_date: '2024-01-15',
          reason: 'Requested room change',
        },
      ]
      setTransferHistory(mockTransfers)

      if (mockBeds.length > 0) {
        setSelectedRoom(mockBeds[0].room_id)
      }
    } catch (error) {
      // Error fetching data
    } finally {
      setLoading(false)
    }
  }

  const handleAssign = (bed: BedAssignment) => {
    setSelectedBed(bed)
    setFormData({
      courier_id: bed.courier_id || 0,
      assigned_date: bed.assigned_date || new Date().toISOString().split('T')[0],
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // API call would go here
      fetchData()
      handleCloseModal()
    } catch (error) {
      // Error assigning bed
    }
  }

  const handleUnassign = async (_bedId: number) => {
    if (window.confirm('Are you sure you want to unassign this bed?')) {
      try {
        // API call would go here
        fetchData()
      } catch (error) {
        // Error unassigning bed
      }
    }
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedBed(null)
    setFormData({
      courier_id: 0,
      assigned_date: new Date().toISOString().split('T')[0],
    })
  }

  const getStatusColor = (status: BedAssignment['status']) => {
    const colors = {
      vacant: 'success',
      occupied: 'primary',
      reserved: 'warning',
    }
    return colors[status] as 'success' | 'primary' | 'warning'
  }

  const filteredBeds = selectedRoom
    ? beds.filter((b) => b.room_id === selectedRoom)
    : beds

  const rooms = Array.from(new Set(beds.map((b) => ({ id: b.room_id, number: b.room_number }))))

  const renderBedLayout = () => {
    const roomBeds = filteredBeds

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {roomBeds.map((bed) => (
          <div
            key={bed.id}
            className={`
              border-2 rounded-lg p-6 cursor-pointer transition-all
              ${
                bed.status === 'vacant'
                  ? 'border-green-500 bg-green-50 hover:bg-green-100'
                  : bed.status === 'occupied'
                  ? 'border-blue-500 bg-blue-50 hover:bg-blue-100'
                  : 'border-yellow-500 bg-yellow-50 hover:bg-yellow-100'
              }
            `}
            onClick={() => handleAssign(bed)}
          >
            <div className="text-center">
              <div className="text-4xl mb-3">
                {bed.status === 'vacant' ? '🛏️' : bed.status === 'occupied' ? '😴' : '⏱️'}
              </div>
              <div className="font-bold text-lg mb-2">
                Bed {bed.room_number}-{bed.bed_number}
              </div>
              <Badge variant={getStatusColor(bed.status)} className="mb-2">
                {bed.status}
              </Badge>
              {bed.courier_name && (
                <div className="text-sm text-gray-700 mt-2">
                  <div className="font-medium">{bed.courier_name}</div>
                  <div className="text-xs text-gray-500">
                    Since {new Date(bed.assigned_date!).toLocaleDateString()}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Bed Assignment</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardContent className="pt-6">
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Select Room</label>
              <Select
                value={selectedRoom?.toString() || ''}
                onChange={(e) => setSelectedRoom(parseInt(e.target.value))}
                className="w-64"
              >
                <option value="">All Rooms</option>
                {rooms.map((room) => (
                  <option key={room.id} value={room.id}>
                    Room {room.number}
                  </option>
                ))}
              </Select>
            </div>

            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : (
              renderBedLayout()
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="font-semibold mb-4">Recent Transfers</h3>
            <div className="space-y-4">
              {transferHistory.map((transfer) => (
                <div key={transfer.id} className="border-l-4 border-blue-500 pl-3 py-2">
                  <div className="font-medium text-sm">{transfer.courier_name}</div>
                  <div className="text-xs text-gray-600">
                    {transfer.from_bed} → {transfer.to_bed}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(transfer.transfer_date).toLocaleDateString()}
                  </div>
                  <div className="text-xs text-gray-500 italic mt-1">
                    {transfer.reason}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Modal
        isOpen={showModal}
        onClose={handleCloseModal}
        title={`Manage Bed ${selectedBed?.room_number}-${selectedBed?.bed_number}`}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Assign Courier</label>
            <Select
              required
              value={formData.courier_id}
              onChange={(e) =>
                setFormData({ ...formData, courier_id: parseInt(e.target.value) })
              }
            >
              <option value="">Select Courier</option>
              {couriers.map((courier) => (
                <option key={courier.id} value={courier.id}>
                  {courier.name}
                </option>
              ))}
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Assignment Date</label>
            <input
              type="date"
              required
              value={formData.assigned_date}
              onChange={(e) =>
                setFormData({ ...formData, assigned_date: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              Assign
            </Button>
            {selectedBed?.courier_id && (
              <Button
                type="button"
                variant="outline"
                onClick={() => handleUnassign(selectedBed.id)}
              >
                Unassign
              </Button>
            )}
            <Button type="button" variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
