import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  Car,
  Calendar,
  MapPin,
  FileText,
  DollarSign,
  Gauge,
  Fuel,
  Wrench,
  Shield,
  Clock,
  User,
  Package,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { Tabs } from '@/components/ui/Tabs'
import { Table } from '@/components/ui/Table'
import { vehiclesAPI } from '@/lib/api'

export default function VehicleDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  // Fetch vehicle details
  const { data: vehicle, isLoading: vehicleLoading, error: vehicleError } = useQuery({
    queryKey: ['vehicle', id],
    queryFn: () => vehiclesAPI.getById(Number(id)),
    enabled: !!id,
  })

  // Fetch vehicle history (maintenance, fuel logs, assignments)
  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['vehicle-history', id],
    queryFn: () => vehiclesAPI.getHistory(Number(id)),
    enabled: !!id,
  })

  // Fetch vehicle logs
  const { data: logs = [], isLoading: logsLoading } = useQuery({
    queryKey: ['vehicle-logs', id],
    queryFn: () => vehiclesAPI.getLogs(Number(id)),
    enabled: !!id,
  })

  if (vehicleLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (vehicleError || !vehicle) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading vehicle details</p>
        <Button onClick={() => navigate('/fleet/vehicles')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Vehicles
        </Button>
      </div>
    )
  }

  // Helper to normalize status
  const normalizeStatus = (status: string) => status?.toUpperCase?.() || ''
  const vehicleStatus = normalizeStatus(vehicle.status)

  // Status badge variant
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success'
      case 'MAINTENANCE':
      case 'REPAIR':
        return 'warning'
      case 'INACTIVE':
        return 'default'
      case 'RETIRED':
        return 'danger'
      default:
        return 'default'
    }
  }

  // Format date helper
  const formatDate = (date: string | null) => {
    if (!date) return 'N/A'
    return new Date(date).toLocaleDateString()
  }

  // Format currency
  const formatCurrency = (amount: number | null) => {
    if (!amount) return 'N/A'
    return `SAR ${amount.toLocaleString()}`
  }

  // Vehicle logs columns
  const logsColumns = [
    {
      key: 'log_date',
      header: 'Date',
      render: (row: any) => formatDate(row.log_date),
    },
    {
      key: 'log_type',
      header: 'Type',
      render: (row: any) => (
        <Badge variant="default">
          {row.log_type?.replace('_', ' ').toUpperCase() || 'N/A'}
        </Badge>
      ),
    },
    {
      key: 'courier',
      header: 'Courier',
      render: (row: any) => row.courier_name || row.courier_id || 'N/A',
    },
    {
      key: 'distance_covered',
      header: 'Distance (km)',
      render: (row: any) => row.distance_covered?.toLocaleString() || '-',
    },
    {
      key: 'fuel_refilled',
      header: 'Fuel (L)',
      render: (row: any) => row.fuel_refilled?.toLocaleString() || '-',
    },
    {
      key: 'fuel_cost',
      header: 'Fuel Cost',
      render: (row: any) => row.fuel_cost ? `SAR ${row.fuel_cost}` : '-',
    },
    {
      key: 'notes',
      header: 'Notes',
      render: (row: any) => (
        <span className="text-sm text-gray-600 truncate max-w-[200px] block">
          {row.notes || '-'}
        </span>
      ),
    },
  ]

  // Maintenance history columns
  const maintenanceColumns = [
    { key: 'date', header: 'Date' },
    {
      key: 'type',
      header: 'Type',
      render: (row: any) => (
        <Badge variant="default">{row.type?.toUpperCase()}</Badge>
      ),
    },
    {
      key: 'cost',
      header: 'Cost',
      render: (row: any) => `SAR ${row.cost?.toLocaleString() || 0}`,
    },
    {
      key: 'mileage',
      header: 'Mileage',
      render: (row: any) => `${row.mileage?.toLocaleString() || 0} km`,
    },
  ]

  // Fuel logs columns
  const fuelColumns = [
    { key: 'date', header: 'Date' },
    {
      key: 'liters',
      header: 'Liters',
      render: (row: any) => `${row.liters?.toLocaleString() || 0} L`,
    },
    {
      key: 'cost',
      header: 'Cost',
      render: (row: any) => `SAR ${row.cost?.toLocaleString() || 0}`,
    },
    {
      key: 'odometer',
      header: 'Odometer',
      render: (row: any) => `${row.odometer?.toLocaleString() || 0} km`,
    },
  ]

  // Assignment history columns
  const assignmentColumns = [
    { key: 'courier', header: 'Courier' },
    { key: 'startDate', header: 'Start Date' },
    { key: 'endDate', header: 'End Date', render: (row: any) => row.endDate || 'Ongoing' },
    { key: 'duration', header: 'Duration' },
  ]

  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      content: (
        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Car className="h-5 w-5" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-500">Plate Number</label>
                    <p className="font-semibold text-lg">{vehicle.plate_number}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Make & Model</label>
                    <p className="font-medium">{vehicle.make} {vehicle.model}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Year</label>
                    <p className="font-medium">{vehicle.year}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-500">Type</label>
                    <p className="font-medium">{vehicle.vehicle_type}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Color</label>
                    <p className="font-medium">{vehicle.color || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Transmission</label>
                    <p className="font-medium">{vehicle.transmission || 'N/A'}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-500">Fuel Type</label>
                    <p className="font-medium">{vehicle.fuel_type || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Engine Capacity</label>
                    <p className="font-medium">{vehicle.engine_capacity || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Ownership</label>
                    <p className="font-medium">{vehicle.ownership_type || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Mileage & Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge className="h-5 w-5" />
                Mileage & Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {vehicle.current_mileage?.toLocaleString() || 0}
                  </p>
                  <p className="text-sm text-gray-600">Current Mileage (km)</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {vehicle.total_trips || 0}
                  </p>
                  <p className="text-sm text-gray-600">Total Trips</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">
                    {vehicle.total_distance?.toLocaleString() || 0}
                  </p>
                  <p className="text-sm text-gray-600">Total Distance (km)</p>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">
                    {vehicle.avg_fuel_consumption || 'N/A'}
                  </p>
                  <p className="text-sm text-gray-600">Avg Fuel (km/L)</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Service & Maintenance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wrench className="h-5 w-5" />
                Service & Maintenance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Last Service Date</span>
                    <span className="font-medium">{formatDate(vehicle.last_service_date)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Last Service Mileage</span>
                    <span className="font-medium">{vehicle.last_service_mileage?.toLocaleString() || 'N/A'} km</span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                    <span className="text-gray-600">Next Service Due</span>
                    <span className="font-medium">{formatDate(vehicle.next_service_due_date)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                    <span className="text-gray-600">Next Service Mileage</span>
                    <span className="font-medium">{vehicle.next_service_due_mileage?.toLocaleString() || 'N/A'} km</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'documents',
      label: 'Documents & Registration',
      content: (
        <div className="space-y-6">
          {/* Registration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Registration Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Registration Number</span>
                    <span className="font-medium">{vehicle.registration_number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Registration Expiry</span>
                    <span className="font-medium">{formatDate(vehicle.registration_expiry_date)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">VIN Number</span>
                    <span className="font-medium font-mono text-sm">{vehicle.vin_number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Engine Number</span>
                    <span className="font-medium font-mono text-sm">{vehicle.engine_number || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Insurance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Insurance Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Insurance Company</span>
                    <span className="font-medium">{vehicle.insurance_company || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Policy Number</span>
                    <span className="font-medium">{vehicle.insurance_policy_number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                    <span className="text-gray-600">Insurance Expiry</span>
                    <span className="font-medium">{formatDate(vehicle.insurance_expiry_date)}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'financial',
      label: 'Financial',
      content: (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Financial Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Purchase Price</span>
                    <span className="font-medium">{formatCurrency(vehicle.purchase_price)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Purchase Date</span>
                    <span className="font-medium">{formatDate(vehicle.purchase_date)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Monthly Lease Cost</span>
                    <span className="font-medium">{formatCurrency(vehicle.monthly_lease_cost)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Depreciation Rate</span>
                    <span className="font-medium">{vehicle.depreciation_rate ? `${vehicle.depreciation_rate}%` : 'N/A'}</span>
                  </div>
                </div>
                {history && (
                  <div className="space-y-4">
                    <div className="text-center p-4 bg-red-50 rounded-lg">
                      <p className="text-2xl font-bold text-red-600">
                        SAR {history.summary?.total_maintenance_cost?.toLocaleString() || 0}
                      </p>
                      <p className="text-sm text-gray-600">Total Maintenance Cost</p>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <p className="text-2xl font-bold text-orange-600">
                        SAR {history.summary?.total_fuel_cost?.toLocaleString() || 0}
                      </p>
                      <p className="text-sm text-gray-600">Total Fuel Cost</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: 'logs',
      label: 'Vehicle Logs',
      content: (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Vehicle Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            {logsLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : logs.length > 0 ? (
              <Table data={logs} columns={logsColumns} />
            ) : (
              <div className="text-center py-8 text-gray-500">
                No vehicle logs found
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'history',
      label: 'History',
      content: (
        <div className="space-y-6">
          {historyLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : (
            <>
              {/* Maintenance History */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wrench className="h-5 w-5" />
                    Maintenance History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {history?.maintenance?.length > 0 ? (
                    <Table data={history.maintenance} columns={maintenanceColumns} />
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No maintenance records found
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Fuel History */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Fuel className="h-5 w-5" />
                    Fuel History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {history?.fuel_logs?.length > 0 ? (
                    <Table data={history.fuel_logs} columns={fuelColumns} />
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No fuel records found
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Assignment History */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Assignment History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {history?.assignments?.length > 0 ? (
                    <Table data={history.assignments} columns={assignmentColumns} />
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No assignment records found
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      ),
    },
    {
      id: 'gps',
      label: 'GPS & Tracking',
      content: (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5" />
              GPS & Tracking Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">GPS Device ID</span>
                  <span className="font-medium font-mono">{vehicle.gps_device_id || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">GPS IMEI</span>
                  <span className="font-medium font-mono">{vehicle.gps_device_imei || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">GPS Active</span>
                  <Badge variant={vehicle.is_gps_active ? 'success' : 'default'}>
                    {vehicle.is_gps_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">Assigned City</span>
                  <span className="font-medium">{vehicle.assigned_to_city || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">Assigned Project</span>
                  <span className="font-medium">{vehicle.assigned_to_project || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">Pool Vehicle</span>
                  <Badge variant={vehicle.is_pool_vehicle ? 'warning' : 'default'}>
                    {vehicle.is_pool_vehicle ? 'Yes' : 'No'}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/fleet/vehicles')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-3">
              <Car className="h-6 w-6" />
              {vehicle.plate_number}
              <Badge variant={getStatusVariant(vehicleStatus)}>
                {vehicleStatus.replace('_', ' ')}
              </Badge>
            </h1>
            <p className="text-gray-600">
              {vehicle.year} {vehicle.make} {vehicle.model} • {vehicle.vehicle_type}
            </p>
          </div>
        </div>
        <Button onClick={() => navigate(`/fleet/vehicles`, { state: { edit: vehicle.id } })}>
          Edit Vehicle
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Gauge className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Mileage</p>
                <p className="font-semibold">{vehicle.current_mileage?.toLocaleString() || 0} km</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Fuel className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Fuel Capacity</p>
                <p className="font-semibold">{vehicle.fuel_capacity || 'N/A'} L</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Package className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Trips</p>
                <p className="font-semibold">{vehicle.total_trips || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Calendar className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Next Service</p>
                <p className="font-semibold">{formatDate(vehicle.next_service_due_date)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Notes */}
      {vehicle.notes && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-700">Notes</p>
                <p className="text-gray-600">{vehicle.notes}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs tabs={tabs} defaultTab="overview" />
    </div>
  )
}
