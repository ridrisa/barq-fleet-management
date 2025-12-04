import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Table } from '@/components/ui/Table'
import { Tabs, Tab } from '@/components/ui/Tabs'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { vehicleHistoryAPI, vehiclesAPI } from '@/lib/api'
import type { Vehicle } from '@/types/fleet'

type MaintenanceEntry = { date: string; type: string; cost: number; mileage: number }
type FuelEntry = { date: string; liters: number; cost: number; odometer: number }
type AssignmentEntry = { courier: string; startDate: string; endDate?: string; duration: string }
type HistorySummary = {
  mileage: number
  total_maintenance_cost: number
  total_fuel_cost: number
  avg_fuel_efficiency: number
}
type VehicleHistoryResponse = {
  summary?: Partial<HistorySummary>
  maintenance?: MaintenanceEntry[]
  fuel_logs?: FuelEntry[]
  assignments?: AssignmentEntry[]
}

const normalizeSummary = (summary?: Partial<HistorySummary>): HistorySummary => ({
  mileage: Number(summary?.mileage) || 0,
  total_maintenance_cost: Number(summary?.total_maintenance_cost) || 0,
  total_fuel_cost: Number(summary?.total_fuel_cost) || 0,
  avg_fuel_efficiency: Number(summary?.avg_fuel_efficiency) || 0,
})

export default function VehicleHistory() {
  const [selectedVehicleId, setSelectedVehicleId] = useState<number | null>(null)

  const vehiclesQuery = useQuery<Vehicle[], Error>({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesAPI.getAll(),
    staleTime: 5 * 60 * 1000,
  })

  useEffect(() => {
    if (!vehiclesQuery.data?.length) {
      setSelectedVehicleId(null)
      return
    }
    const exists = vehiclesQuery.data.some((vehicle) => vehicle.id === selectedVehicleId)
    if (!exists) {
      setSelectedVehicleId(vehiclesQuery.data[0].id)
    }
  }, [vehiclesQuery.data, selectedVehicleId])

  const historyQuery = useQuery<VehicleHistoryResponse, Error>({
    queryKey: ['vehicleHistory', selectedVehicleId],
    enabled: selectedVehicleId !== null,
    queryFn: async () => {
      if (selectedVehicleId === null) {
        throw new Error('Vehicle not selected')
      }
      return vehicleHistoryAPI.getHistory(selectedVehicleId)
    },
  })

  const summary = useMemo(
    () => normalizeSummary(historyQuery.data?.summary),
    [historyQuery.data]
  )

  const vehicleOptions = useMemo(
    () =>
      (vehiclesQuery.data ?? []).map((v) => ({
        value: String(v.id),
        label: `${v.make} ${v.model} - ${v.plate_number}`,
      })),
    [vehiclesQuery.data]
  )

  const maintenanceHistory = historyQuery.data?.maintenance ?? []
  const fuelHistory = historyQuery.data?.fuel_logs ?? []
  const assignmentHistory = historyQuery.data?.assignments ?? []

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

  if (vehiclesQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (vehiclesQuery.isError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading vehicles: {vehiclesQuery.error.message}</p>
      </div>
    )
  }

  if (!vehicleOptions.length) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">No vehicles found. Add a vehicle to view history.</p>
      </div>
    )
  }

  if (historyQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (historyQuery.isError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading vehicle history: {historyQuery.error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Vehicle History</h1>
        <Select
          options={vehicleOptions}
          value={selectedVehicleId !== null ? String(selectedVehicleId) : ''}
          onChange={(e) => {
            const value = e.target.value
            if (!value) {
              setSelectedVehicleId(null)
              return
            }
            const nextId = Number(value)
            setSelectedVehicleId(Number.isFinite(nextId) ? nextId : null)
          }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{summary.mileage} km</div>
            <p className="text-sm text-gray-600">Current Mileage</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">SAR {summary.total_maintenance_cost}</div>
            <p className="text-sm text-gray-600">Total Maintenance</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">SAR {summary.total_fuel_cost}</div>
            <p className="text-sm text-gray-600">Total Fuel Cost</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{summary.avg_fuel_efficiency} km/L</div>
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
