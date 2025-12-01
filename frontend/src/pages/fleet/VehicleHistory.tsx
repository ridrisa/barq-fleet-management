import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Table } from '@/components/ui/Table'
import { Tabs, Tab } from '@/components/ui/Tabs'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { vehicleHistoryAPI, vehiclesAPI } from '@/lib/api'

export default function VehicleHistory() {
  const [selectedVehicle, setSelectedVehicle] = useState('')
  const [vehicles, setVehicles] = useState<any[]>([])

  useEffect(() => {
    const loadVehicles = async () => {
      try {
        const data = await vehiclesAPI.getAll()
        setVehicles(data)
        if (data.length > 0) {
          setSelectedVehicle(String(data[0].id))
        }
      } catch (error) {
        console.error('Failed to load vehicles:', error)
      }
    }
    loadVehicles()
  }, [])

  const { data: history, isLoading, error } = useQuery({
    queryKey: ['vehicleHistory', selectedVehicle],
    queryFn: () => vehicleHistoryAPI.getHistory(Number(selectedVehicle)),
    enabled: !!selectedVehicle,
  })

  const maintenanceHistory = history?.maintenance || []
  const fuelHistory = history?.fuel_logs || []
  const assignmentHistory = history?.assignments || []

  const tabs: Tab[] = [
    {
      id: 'maintenance',
      label: 'Maintenance',
      content: (
        <Table
          data={maintenanceHistory}
          columns={[
            { key: 'date', header: 'Date' },
            { key: 'type', header: 'Type' },
            { key: 'cost', header: 'Cost (SAR)' },
            { key: 'mileage', header: 'Mileage (km)' },
          ]}
        />
      ),
    },
    {
      id: 'fuel',
      label: 'Fuel',
      content: (
        <Table
          data={fuelHistory}
          columns={[
            { key: 'date', header: 'Date' },
            { key: 'liters', header: 'Liters' },
            { key: 'cost', header: 'Cost (SAR)' },
            { key: 'odometer', header: 'Odometer (km)' },
          ]}
        />
      ),
    },
    {
      id: 'assignments',
      label: 'Assignments',
      content: (
        <Table
          data={assignmentHistory}
          columns={[
            { key: 'courier', header: 'Courier' },
            { key: 'startDate', header: 'Start Date' },
            { key: 'endDate', header: 'End Date' },
            { key: 'duration', header: 'Duration' },
          ]}
        />
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
        <p className="text-red-800">Error loading vehicle history: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Vehicle History</h1>
        <Select
          options={vehicles.map((v) => ({ value: String(v.id), label: `${v.make} ${v.model} - ${v.plate_number}` }))}
          value={selectedVehicle}
          onChange={(e) => setSelectedVehicle(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{history?.summary.current_mileage || 0} km</div>
            <p className="text-sm text-gray-600">Current Mileage</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">SAR {history?.summary.total_maintenance_cost || 0}</div>
            <p className="text-sm text-gray-600">Total Maintenance</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">SAR {history?.summary.total_fuel_cost || 0}</div>
            <p className="text-sm text-gray-600">Total Fuel Cost</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{history?.summary.avg_fuel_efficiency || 0} km/L</div>
            <p className="text-sm text-gray-600">Avg Efficiency</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>History Details</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs tabs={tabs} />
        </CardContent>
      </Card>
    </div>
  )
}