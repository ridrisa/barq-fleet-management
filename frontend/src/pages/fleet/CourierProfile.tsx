import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  ArrowLeft,
  User,
  Phone,
  Mail,
  MapPin,
  Calendar,
  CreditCard,
  Car,
  FileText,
  DollarSign,
  Clock,
  AlertTriangle,
  Building,
  TrendingUp,
  Package,
  History,
  Navigation,
  Shirt,
  Smartphone,
  Wrench,
  Wallet,
  ClipboardList,
  Fuel,
  Route,
  RefreshCw,
  Gauge,
  Radio,
  CheckCircle,
  XCircle,
  Gift,
  Truck,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { couriersAPI, vehiclesAPI, leavesAPI, loansAPI, assetsAPI, assignmentsAPI, fmsAPI, salaryAPI, vehicleLogsAPI, fmsSyncAPI, attendanceAPI, deliveriesAPI, bonusesAPI } from '@/lib/api'
import { CourierProfileLayout, LayoutSelector, type TabGroup } from '@/components/layouts/CourierProfileLayouts'
import { useCourierProfileLayout } from '@/hooks/useUserPreferences'

// Custom marker icon for courier location
const createCourierMarkerIcon = (isMoving: boolean) => {
  const color = isMoving ? '#22c55e' : '#f59e0b'
  const iconHtml = `
    <div style="
      background: ${color};
      width: 40px;
      height: 40px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 4px solid white;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
      ${isMoving ? 'animation: pulse 2s infinite;' : ''}
    ">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
        ${isMoving
          ? '<path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>'
          : '<circle cx="12" cy="12" r="6"/>'
        }
      </svg>
    </div>
  `
  return L.divIcon({
    html: iconHtml,
    className: 'courier-marker',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  })
}

// Animation styles for marker
const markerStyles = `
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.15); }
    100% { transform: scale(1); }
  }
  .courier-marker {
    background: transparent;
    border: none;
  }
`

export default function CourierProfile() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [isRefreshingLocation, setIsRefreshingLocation] = useState(false)
  const { layout, setLayout } = useCourierProfileLayout()

  // Fetch courier details
  const { data: courier, isLoading: courierLoading, error: courierError } = useQuery({
    queryKey: ['courier', id],
    queryFn: async () => {
      const response = await couriersAPI.getById(Number(id))
      return response
    },
    enabled: !!id,
  })

  // Fetch related vehicles
  const { data: vehicles = [] } = useQuery({
    queryKey: ['vehicles'],
    queryFn: vehiclesAPI.getAll,
  })

  // Fetch leaves for this courier
  const { data: leaves = [] } = useQuery({
    queryKey: ['leaves'],
    queryFn: leavesAPI.getAll,
  })

  // Fetch loans for this courier
  const { data: loans = [] } = useQuery({
    queryKey: ['loans'],
    queryFn: loansAPI.getAll,
  })

  // Fetch assets for this courier
  const { data: assets = [] } = useQuery({
    queryKey: ['assets'],
    queryFn: assetsAPI.getAll,
  })

  // Fetch vehicle assignments history
  const { data: assignments = [] } = useQuery({
    queryKey: ['assignments'],
    queryFn: assignmentsAPI.getAll,
  })

  // Fetch FMS vehicle data for GPS tracking (if vehicle has GPS)
  const { data: fmsVehicle } = useQuery({
    queryKey: ['fms-vehicle', courier?.current_vehicle?.plate_number],
    queryFn: async () => {
      if (!courier?.current_vehicle?.plate_number) return null
      try {
        return await fmsAPI.getAssetByPlate(courier.current_vehicle.plate_number)
      } catch {
        return null
      }
    },
    enabled: !!courier?.current_vehicle?.plate_number,
  })

  // Fetch salaries for this courier
  const { data: salaries = [] } = useQuery({
    queryKey: ['salaries'],
    queryFn: salaryAPI.getAll,
  })

  // Fetch vehicle logs for this courier
  const { data: vehicleLogs = [] } = useQuery({
    queryKey: ['vehicle-logs'],
    queryFn: vehicleLogsAPI.getAll,
  })

  // Fetch attendance records for this courier
  const { data: attendance = [] } = useQuery({
    queryKey: ['attendance'],
    queryFn: attendanceAPI.getAll,
  })

  // Fetch deliveries for this courier
  const { data: deliveries = [] } = useQuery({
    queryKey: ['deliveries'],
    queryFn: deliveriesAPI.getAll,
  })

  // Fetch bonuses for this courier
  const { data: bonuses = [] } = useQuery({
    queryKey: ['bonuses'],
    queryFn: bonusesAPI.getAll,
  })

  // Fetch live location from FMS using courier's barq_id
  const { data: liveLocationData, refetch: refetchLocation } = useQuery({
    queryKey: ['courier-live-location', courier?.barq_id],
    queryFn: async () => {
      if (!courier?.barq_id) return null
      try {
        const response = await fmsSyncAPI.getLiveLocations()
        const locations = response.locations || []
        return locations.find((loc: any) => loc.barq_id === courier.barq_id) || null
      } catch {
        return null
      }
    },
    enabled: !!courier?.barq_id,
    refetchInterval: 30000,
  })

  // Manual refresh location handler
  const handleRefreshLocation = async () => {
    setIsRefreshingLocation(true)
    await refetchLocation()
    setIsRefreshingLocation(false)
  }

  if (courierLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (courierError || !courier) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading courier profile</p>
        <Button onClick={() => navigate(-1)} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Go Back
        </Button>
      </div>
    )
  }

  // Filter related data
  const courierVehicle = vehicles.find((v: any) => v.id === courier.current_vehicle_id)
  const courierLeaves = leaves.filter((l: any) => l.courier_id === courier.id)
  const courierLoans = loans.filter((l: any) => l.courier_id === courier.id)
  const courierAssets = assets.filter((a: any) => a.courier_id === courier.id)
  const courierVehicleHistory = assignments.filter((a: any) => a.courier_id === courier.id)
    .sort((a: any, b: any) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime())
  const courierSalaries = salaries.filter((s: any) => s.courier_id === courier.id)
    .sort((a: any, b: any) => {
      const dateA = new Date(a.year, a.month - 1)
      const dateB = new Date(b.year, b.month - 1)
      return dateB.getTime() - dateA.getTime()
    })
  const courierVehicleLogs = vehicleLogs.filter((l: any) => l.courier_id === courier.id)
    .sort((a: any, b: any) => new Date(b.log_date).getTime() - new Date(a.log_date).getTime())
  const courierAttendance = attendance.filter((a: any) => a.courier_id === courier.id)
    .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime())
  const courierDeliveries = deliveries.filter((d: any) => d.courier_id === courier.id)
    .sort((a: any, b: any) => new Date(b.created_at || b.delivery_date).getTime() - new Date(a.created_at || a.delivery_date).getTime())
  const courierBonuses = bonuses.filter((b: any) => b.courier_id === courier.id)
    .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  // Get asset type icon
  const getAssetIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'uniform':
        return <Shirt className="h-4 w-4" />
      case 'mobile_device':
        return <Smartphone className="h-4 w-4" />
      case 'equipment':
      case 'tools':
        return <Wrench className="h-4 w-4" />
      default:
        return <Package className="h-4 w-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      active: 'success',
      on_leave: 'warning',
      inactive: 'danger',
      terminated: 'danger',
      onboarding: 'default',
    }
    return statusMap[status?.toLowerCase()] || 'default'
  }

  // Tab content components
  const LiveLocationContent = (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Radio className="h-5 w-5 text-green-600" />
            Live GPS Location
          </CardTitle>
          <Button variant="outline" size="sm" onClick={handleRefreshLocation} disabled={isRefreshingLocation}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshingLocation ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <style>{markerStyles}</style>
        {liveLocationData ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 flex-wrap">
              <span className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium ${
                liveLocationData.speed_kmh > 5 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {liveLocationData.speed_kmh > 5 ? <><Navigation className="w-4 h-4" />Moving</> : <><Clock className="w-4 h-4" />Idle</>}
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                <Gauge className="w-4 h-4" />{liveLocationData.speed_kmh?.toFixed(0) || 0} km/h
              </span>
              {liveLocationData.gps_timestamp && (
                <span className="text-sm text-gray-500">Last update: {new Date(liveLocationData.gps_timestamp).toLocaleString()}</span>
              )}
            </div>
            <div className="h-[400px] rounded-lg overflow-hidden border">
              <MapContainer center={[liveLocationData.position.latitude, liveLocationData.position.longitude]} zoom={15} className="h-full w-full" scrollWheelZoom={true}>
                <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <Marker position={[liveLocationData.position.latitude, liveLocationData.position.longitude]} icon={createCourierMarkerIcon(liveLocationData.speed_kmh > 5)}>
                  <Popup>
                    <div className="min-w-[200px]">
                      <div className="font-semibold text-gray-900 mb-2 pb-2 border-b">{courier?.full_name || liveLocationData.driver_name || 'Unknown'}</div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between"><span className="text-gray-500">BARQ ID:</span><span className="font-medium">{liveLocationData.barq_id}</span></div>
                        <div className="flex justify-between"><span className="text-gray-500">Speed:</span><span className={`font-medium ${liveLocationData.speed_kmh > 5 ? 'text-green-600' : 'text-yellow-600'}`}>{liveLocationData.speed_kmh?.toFixed(1) || 0} km/h</span></div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              </MapContainer>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Latitude</p><p className="font-medium">{liveLocationData.position.latitude?.toFixed(6)}</p></div>
              <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Longitude</p><p className="font-medium">{liveLocationData.position.longitude?.toFixed(6)}</p></div>
              <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">FMS Asset ID</p><p className="font-medium">{liveLocationData.fms_asset_id}</p></div>
              <div className="p-3 bg-gray-50 rounded-lg"><p className="text-xs text-gray-500">Vehicle</p><p className="font-medium">{liveLocationData.asset_name || 'N/A'}</p></div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <MapPin className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium text-gray-600">No Live Location Available</p>
            <p className="text-sm text-gray-500 mt-2">This courier is not connected to FMS GPS tracking or the device is offline.</p>
          </div>
        )}
      </CardContent>
    </Card>
  )

  const VehicleContent = (
    <Card>
      <CardHeader><CardTitle>Assigned Vehicle</CardTitle></CardHeader>
      <CardContent>
        {courierVehicle ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div><p className="text-sm text-gray-500">Plate Number</p><p className="font-medium text-lg">{courierVehicle.plate_number}</p></div>
              <div><p className="text-sm text-gray-500">Make & Model</p><p className="font-medium">{courierVehicle.make} {courierVehicle.model} ({courierVehicle.year})</p></div>
              <div><p className="text-sm text-gray-500">Status</p><Badge variant={courierVehicle.status === 'active' ? 'success' : 'warning'}>{courierVehicle.status}</Badge></div>
              <div><p className="text-sm text-gray-500">Current Mileage</p><p className="font-medium">{courierVehicle.current_mileage?.toLocaleString() || 0} km</p></div>
              <div><p className="text-sm text-gray-500">Vehicle Type</p><p className="font-medium">{courierVehicle.vehicle_type}</p></div>
              <div><p className="text-sm text-gray-500">Color</p><p className="font-medium">{courierVehicle.color || 'N/A'}</p></div>
            </div>
            {fmsVehicle && (
              <div className="mt-6 pt-6 border-t">
                <h4 className="font-medium mb-4 flex items-center gap-2"><Navigation className="h-4 w-4 text-blue-600" />Live GPS Tracking</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg"><p className="text-xs text-gray-500">FMS Asset ID</p><p className="font-medium">{fmsVehicle.AssetId || fmsVehicle.Id || 'N/A'}</p></div>
                  <div className="p-3 bg-green-50 rounded-lg"><p className="text-xs text-gray-500">GPS Status</p><p className="font-medium text-green-600">{fmsVehicle.IsOnline ? 'Online' : 'Offline'}</p></div>
                  <div className="p-3 bg-purple-50 rounded-lg"><p className="text-xs text-gray-500">Current Speed</p><p className="font-medium">{fmsVehicle.Speed || 0} km/h</p></div>
                  <div className="p-3 bg-orange-50 rounded-lg"><p className="text-xs text-gray-500">Last Update</p><p className="font-medium text-sm">{fmsVehicle.LastUpdated ? new Date(fmsVehicle.LastUpdated).toLocaleString() : 'N/A'}</p></div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500"><Car className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No vehicle assigned to this courier</p></div>
        )}
      </CardContent>
    </Card>
  )

  const VehicleHistoryContent = (
    <Card>
      <CardHeader><CardTitle>Vehicle Assignment History</CardTitle></CardHeader>
      <CardContent>
        {courierVehicleHistory.length > 0 ? (
          <div className="space-y-4">
            {courierVehicleHistory.map((assignment: any) => {
              const vehicle = vehicles.find((v: any) => v.id === assignment.vehicle_id)
              return (
                <div key={assignment.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg"><Car className="h-5 w-5 text-blue-600" /></div>
                      <div>
                        <p className="font-medium">{vehicle?.plate_number || 'Unknown Vehicle'}</p>
                        <p className="text-sm text-gray-500">{vehicle ? `${vehicle.make} ${vehicle.model} (${vehicle.year})` : 'Details not available'}</p>
                      </div>
                    </div>
                    <Badge variant={assignment.status === 'active' ? 'success' : assignment.status === 'completed' ? 'default' : 'warning'}>{assignment.status || 'Unknown'}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div><p className="text-gray-500">Start Date</p><p className="font-medium">{assignment.start_date ? new Date(assignment.start_date).toLocaleDateString() : 'N/A'}</p></div>
                    <div><p className="text-gray-500">End Date</p><p className="font-medium">{assignment.end_date ? new Date(assignment.end_date).toLocaleDateString() : 'Ongoing'}</p></div>
                    <div><p className="text-gray-500">Start Mileage</p><p className="font-medium">{assignment.start_mileage?.toLocaleString() || 'N/A'} km</p></div>
                    <div><p className="text-gray-500">End Mileage</p><p className="font-medium">{assignment.end_mileage?.toLocaleString() || 'N/A'} km</p></div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500"><History className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No vehicle assignment history found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const LogsContent = (
    <Card>
      <CardHeader><CardTitle>Vehicle Logs & Trips</CardTitle></CardHeader>
      <CardContent>
        {courierVehicleLogs.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-blue-50 rounded-lg text-center"><p className="text-2xl font-bold text-blue-600">{courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.distance_covered) || 0), 0).toLocaleString()} km</p><p className="text-sm text-gray-500">Total Distance</p></div>
              <div className="p-4 bg-green-50 rounded-lg text-center"><p className="text-2xl font-bold text-green-600">{courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.number_of_deliveries) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Total Deliveries</p></div>
              <div className="p-4 bg-orange-50 rounded-lg text-center"><p className="text-2xl font-bold text-orange-600">SAR {courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.fuel_cost) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Total Fuel Cost</p></div>
              <div className="p-4 bg-purple-50 rounded-lg text-center"><p className="text-2xl font-bold text-purple-600">SAR {courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.revenue_generated) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Revenue Generated</p></div>
            </div>
            <div className="space-y-4">
              {courierVehicleLogs.slice(0, 10).map((log: any) => (
                <div key={log.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${log.log_type === 'fuel_refill' ? 'bg-orange-100' : log.log_type === 'delivery' ? 'bg-green-100' : 'bg-blue-100'}`}>
                        {log.log_type === 'fuel_refill' ? <Fuel className="h-5 w-5 text-orange-600" /> : <Route className="h-5 w-5 text-blue-600" />}
                      </div>
                      <div>
                        <p className="font-medium capitalize">{log.log_type?.replace('_', ' ') || 'Daily Log'}</p>
                        <p className="text-sm text-gray-500">{log.log_date ? new Date(log.log_date).toLocaleDateString() : 'N/A'}</p>
                      </div>
                    </div>
                    <Badge variant={log.has_issues ? 'danger' : 'success'}>{log.vehicle_condition || 'Good'}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div><p className="text-gray-500">Distance</p><p className="font-medium">{Number(log.distance_covered || 0).toLocaleString()} km</p></div>
                    <div><p className="text-gray-500">Deliveries</p><p className="font-medium">{log.number_of_deliveries || 0}</p></div>
                    <div><p className="text-gray-500">Fuel Used</p><p className="font-medium">{Number(log.fuel_refilled || 0).toLocaleString()} L</p></div>
                    <div><p className="text-gray-500">Revenue</p><p className="font-medium">SAR {Number(log.revenue_generated || 0).toLocaleString()}</p></div>
                  </div>
                </div>
              ))}
            </div>
            {courierVehicleLogs.length > 10 && <div className="mt-4 text-center"><p className="text-sm text-gray-500">Showing 10 of {courierVehicleLogs.length} logs</p></div>}
          </>
        ) : (
          <div className="text-center py-8 text-gray-500"><ClipboardList className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No vehicle logs found for this courier</p></div>
        )}
      </CardContent>
    </Card>
  )

  const SalariesContent = (
    <Card>
      <CardHeader><CardTitle>Salary History</CardTitle></CardHeader>
      <CardContent>
        {courierSalaries.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-green-50 rounded-lg text-center"><p className="text-2xl font-bold text-green-600">SAR {courierSalaries[0]?.net_salary?.toLocaleString() || 0}</p><p className="text-sm text-gray-500">Latest Net Salary</p></div>
              <div className="p-4 bg-blue-50 rounded-lg text-center"><p className="text-2xl font-bold text-blue-600">SAR {courierSalaries[0]?.gross_salary?.toLocaleString() || 0}</p><p className="text-sm text-gray-500">Gross Salary</p></div>
              <div className="p-4 bg-orange-50 rounded-lg text-center"><p className="text-2xl font-bold text-orange-600">SAR {courierSalaries.reduce((sum: number, s: any) => sum + (Number(s.deductions) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Total Deductions</p></div>
              <div className="p-4 bg-purple-50 rounded-lg text-center"><p className="text-2xl font-bold text-purple-600">{courierSalaries.length}</p><p className="text-sm text-gray-500">Months Recorded</p></div>
            </div>
            <div className="space-y-4">
              {courierSalaries.map((salary: any) => (
                <div key={salary.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div><p className="font-medium text-lg">{new Date(salary.year, salary.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</p><p className="text-sm text-gray-500">Payment: {salary.payment_date ? new Date(salary.payment_date).toLocaleDateString() : 'Pending'}</p></div>
                    <div className="text-right"><p className="text-2xl font-bold text-green-600">SAR {Number(salary.net_salary || 0).toLocaleString()}</p><p className="text-xs text-gray-500">Net Salary</p></div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                    <div><p className="text-gray-500">Base Salary</p><p className="font-medium">SAR {Number(salary.base_salary || 0).toLocaleString()}</p></div>
                    <div><p className="text-gray-500">Allowances</p><p className="font-medium text-green-600">+SAR {Number(salary.allowances || 0).toLocaleString()}</p></div>
                    <div><p className="text-gray-500">Deductions</p><p className="font-medium text-red-600">-SAR {Number(salary.deductions || 0).toLocaleString()}</p></div>
                    <div><p className="text-gray-500">Loan Deduction</p><p className="font-medium text-orange-600">-SAR {Number(salary.loan_deduction || 0).toLocaleString()}</p></div>
                    <div><p className="text-gray-500">GOSI</p><p className="font-medium text-purple-600">-SAR {Number(salary.gosi_employee || 0).toLocaleString()}</p></div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-gray-500"><Wallet className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No salary records found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const LoansContent = (
    <Card>
      <CardHeader><CardTitle>Loan History</CardTitle></CardHeader>
      <CardContent>
        {courierLoans.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-blue-50 rounded-lg text-center"><p className="text-2xl font-bold text-blue-600">SAR {courierLoans.reduce((sum: number, l: any) => sum + (Number(l.amount) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Total Loans</p></div>
              <div className="p-4 bg-orange-50 rounded-lg text-center"><p className="text-2xl font-bold text-orange-600">SAR {courierLoans.reduce((sum: number, l: any) => sum + (Number(l.outstanding_balance) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Outstanding Balance</p></div>
              <div className="p-4 bg-green-50 rounded-lg text-center"><p className="text-2xl font-bold text-green-600">{courierLoans.filter((l: any) => l.status === 'active').length}</p><p className="text-sm text-gray-500">Active Loans</p></div>
            </div>
            <div className="space-y-4">
              {courierLoans.map((loan: any) => (
                <div key={loan.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div><p className="font-medium text-lg">SAR {Number(loan.amount || 0).toLocaleString()}</p><p className="text-sm text-gray-500">Monthly: SAR {Number(loan.monthly_deduction || 0).toLocaleString()}</p></div>
                    <Badge variant={loan.status === 'approved' || loan.status === 'paid' || loan.status === 'active' ? 'success' : loan.status === 'rejected' ? 'danger' : 'warning'}>{loan.status || 'pending'}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div><p className="text-gray-500">Start Date</p><p className="font-medium">{loan.start_date ? new Date(loan.start_date).toLocaleDateString() : 'N/A'}</p></div>
                    <div><p className="text-gray-500">Outstanding</p><p className="font-medium">SAR {Number(loan.outstanding_balance || 0).toLocaleString()}</p></div>
                    <div><p className="text-gray-500">End Date</p><p className="font-medium">{loan.end_date ? new Date(loan.end_date).toLocaleDateString() : 'N/A'}</p></div>
                    <div><p className="text-gray-500">Reason</p><p className="font-medium truncate">{loan.reason || 'N/A'}</p></div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-gray-500"><DollarSign className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No loan records found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const BonusesContent = (
    <Card>
      <CardHeader><CardTitle>Bonus History</CardTitle></CardHeader>
      <CardContent>
        {courierBonuses.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-green-50 rounded-lg text-center"><p className="text-2xl font-bold text-green-600">SAR {courierBonuses.reduce((sum: number, b: any) => sum + (Number(b.amount) || 0), 0).toLocaleString()}</p><p className="text-sm text-gray-500">Total Bonuses</p></div>
              <div className="p-4 bg-blue-50 rounded-lg text-center"><p className="text-2xl font-bold text-blue-600">{courierBonuses.filter((b: any) => b.status === 'paid').length}</p><p className="text-sm text-gray-500">Paid</p></div>
              <div className="p-4 bg-yellow-50 rounded-lg text-center"><p className="text-2xl font-bold text-yellow-600">{courierBonuses.filter((b: any) => b.status === 'pending' || b.status === 'approved').length}</p><p className="text-sm text-gray-500">Pending</p></div>
            </div>
            <div className="space-y-3">
              {courierBonuses.map((bonus: any) => (
                <div key={bonus.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 rounded-lg"><Gift className="h-5 w-5 text-green-600" /></div>
                      <div><p className="font-medium capitalize">{bonus.bonus_type?.replace('_', ' ') || 'Bonus'}</p><p className="text-sm text-gray-500">{bonus.created_at ? new Date(bonus.created_at).toLocaleDateString() : 'N/A'}</p></div>
                    </div>
                    <div className="text-right"><p className="text-xl font-bold text-green-600">SAR {Number(bonus.amount || 0).toLocaleString()}</p><Badge variant={bonus.status === 'paid' ? 'success' : bonus.status === 'approved' ? 'primary' : bonus.status === 'rejected' ? 'danger' : 'warning'}>{bonus.status || 'pending'}</Badge></div>
                  </div>
                  {bonus.reason && <p className="text-sm text-gray-600 mt-2">{bonus.reason}</p>}
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="text-center py-8 text-gray-500"><Gift className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No bonus records found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const LeavesContent = (
    <Card>
      <CardHeader><CardTitle>Leave History</CardTitle></CardHeader>
      <CardContent>
        {courierLeaves.length > 0 ? (
          <div className="space-y-4">
            {courierLeaves.map((leave: any) => (
              <div key={leave.id} className="p-4 border rounded-lg flex items-center justify-between">
                <div>
                  <p className="font-medium">{leave.leave_type || 'Leave'}</p>
                  <p className="text-sm text-gray-500">{leave.start_date ? new Date(leave.start_date).toLocaleDateString() : 'N/A'} - {leave.end_date ? new Date(leave.end_date).toLocaleDateString() : 'N/A'}</p>
                  <p className="text-sm text-gray-500">{leave.reason || 'No reason provided'}</p>
                </div>
                <Badge variant={leave.status === 'approved' ? 'success' : leave.status === 'rejected' ? 'danger' : 'warning'}>{leave.status || 'pending'}</Badge>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500"><Clock className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No leave records found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const AttendanceContent = (
    <Card>
      <CardHeader><CardTitle>Attendance History</CardTitle></CardHeader>
      <CardContent>
        {courierAttendance.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-green-50 rounded-lg text-center"><p className="text-2xl font-bold text-green-600">{courierAttendance.filter((a: any) => a.status === 'present').length}</p><p className="text-sm text-gray-500">Present</p></div>
              <div className="p-4 bg-red-50 rounded-lg text-center"><p className="text-2xl font-bold text-red-600">{courierAttendance.filter((a: any) => a.status === 'absent').length}</p><p className="text-sm text-gray-500">Absent</p></div>
              <div className="p-4 bg-yellow-50 rounded-lg text-center"><p className="text-2xl font-bold text-yellow-600">{courierAttendance.filter((a: any) => a.status === 'late').length}</p><p className="text-sm text-gray-500">Late</p></div>
              <div className="p-4 bg-blue-50 rounded-lg text-center"><p className="text-2xl font-bold text-blue-600">{courierAttendance.filter((a: any) => a.status === 'on_leave').length}</p><p className="text-sm text-gray-500">On Leave</p></div>
            </div>
            <div className="space-y-2">
              {courierAttendance.slice(0, 20).map((record: any) => (
                <div key={record.id} className="p-3 border rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${record.status === 'present' ? 'bg-green-100' : record.status === 'absent' ? 'bg-red-100' : record.status === 'late' ? 'bg-yellow-100' : 'bg-blue-100'}`}>
                      {record.status === 'present' ? <CheckCircle className="h-4 w-4 text-green-600" /> : record.status === 'absent' ? <XCircle className="h-4 w-4 text-red-600" /> : <Clock className="h-4 w-4 text-yellow-600" />}
                    </div>
                    <div>
                      <p className="font-medium">{record.date ? new Date(record.date).toLocaleDateString() : 'N/A'}</p>
                      {record.check_in && <p className="text-xs text-gray-500">In: {record.check_in} {record.check_out && `| Out: ${record.check_out}`}</p>}
                    </div>
                  </div>
                  <Badge variant={record.status === 'present' ? 'success' : record.status === 'absent' ? 'danger' : record.status === 'late' ? 'warning' : 'default'}>{record.status?.replace('_', ' ') || 'Unknown'}</Badge>
                </div>
              ))}
            </div>
            {courierAttendance.length > 20 && <div className="mt-4 text-center"><p className="text-sm text-gray-500">Showing 20 of {courierAttendance.length} records</p></div>}
          </>
        ) : (
          <div className="text-center py-8 text-gray-500"><CheckCircle className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No attendance records found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const DeliveriesContent = (
    <Card>
      <CardHeader><CardTitle>Delivery History</CardTitle></CardHeader>
      <CardContent>
        {courierDeliveries.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-blue-50 rounded-lg text-center"><p className="text-2xl font-bold text-blue-600">{courierDeliveries.length}</p><p className="text-sm text-gray-500">Total Deliveries</p></div>
              <div className="p-4 bg-green-50 rounded-lg text-center"><p className="text-2xl font-bold text-green-600">{courierDeliveries.filter((d: any) => d.status === 'delivered').length}</p><p className="text-sm text-gray-500">Completed</p></div>
              <div className="p-4 bg-yellow-50 rounded-lg text-center"><p className="text-2xl font-bold text-yellow-600">{courierDeliveries.filter((d: any) => d.status === 'in_transit' || d.status === 'pending').length}</p><p className="text-sm text-gray-500">In Progress</p></div>
              <div className="p-4 bg-red-50 rounded-lg text-center"><p className="text-2xl font-bold text-red-600">{courierDeliveries.filter((d: any) => d.status === 'failed' || d.status === 'returned').length}</p><p className="text-sm text-gray-500">Failed/Returned</p></div>
            </div>
            <div className="space-y-3">
              {courierDeliveries.slice(0, 15).map((delivery: any) => (
                <div key={delivery.id} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${delivery.status === 'delivered' ? 'bg-green-100' : delivery.status === 'in_transit' ? 'bg-blue-100' : delivery.status === 'failed' ? 'bg-red-100' : 'bg-gray-100'}`}>
                        <Truck className={`h-5 w-5 ${delivery.status === 'delivered' ? 'text-green-600' : delivery.status === 'in_transit' ? 'text-blue-600' : delivery.status === 'failed' ? 'text-red-600' : 'text-gray-600'}`} />
                      </div>
                      <div>
                        <p className="font-medium">{delivery.tracking_number || `DEL-${delivery.id?.toString().padStart(5, '0')}`}</p>
                        <p className="text-sm text-gray-500">{delivery.delivery_date ? new Date(delivery.delivery_date).toLocaleDateString() : 'N/A'}</p>
                      </div>
                    </div>
                    <Badge variant={delivery.status === 'delivered' ? 'success' : delivery.status === 'in_transit' ? 'primary' : delivery.status === 'failed' || delivery.status === 'returned' ? 'danger' : 'warning'}>{delivery.status?.replace('_', ' ') || 'pending'}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div><p className="text-gray-500">Customer</p><p className="font-medium truncate">{delivery.customer_name || delivery.receiver_name || 'N/A'}</p></div>
                    <div><p className="text-gray-500">Address</p><p className="font-medium truncate">{delivery.delivery_address || 'N/A'}</p></div>
                    <div><p className="text-gray-500">COD Amount</p><p className="font-medium">SAR {Number(delivery.cod_amount || 0).toLocaleString()}</p></div>
                    <div><p className="text-gray-500">Payment</p><p className="font-medium capitalize">{delivery.payment_method || delivery.payment_status || 'N/A'}</p></div>
                  </div>
                </div>
              ))}
            </div>
            {courierDeliveries.length > 15 && <div className="mt-4 text-center"><p className="text-sm text-gray-500">Showing 15 of {courierDeliveries.length} deliveries</p></div>}
          </>
        ) : (
          <div className="text-center py-8 text-gray-500"><Truck className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No delivery records found</p></div>
        )}
      </CardContent>
    </Card>
  )

  const AssetsContent = (
    <Card>
      <CardHeader><CardTitle>Assigned Assets</CardTitle></CardHeader>
      <CardContent>
        {courierAssets.length > 0 ? (
          <div className="space-y-4">
            {courierAssets.map((asset: any) => (
              <div key={asset.id} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg">{getAssetIcon(asset.asset_type)}</div>
                    <div><p className="font-medium capitalize">{asset.asset_type?.replace('_', ' ') || 'Asset'}</p><p className="text-sm text-gray-500">Issued: {asset.issue_date ? new Date(asset.issue_date).toLocaleDateString() : 'N/A'}</p></div>
                  </div>
                  <Badge variant={asset.status === 'assigned' ? 'success' : asset.status === 'returned' ? 'default' : asset.status === 'damaged' || asset.status === 'lost' ? 'danger' : 'warning'}>{asset.status || 'Unknown'}</Badge>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div><p className="text-gray-500">Condition</p><p className="font-medium capitalize">{asset.condition || 'N/A'}</p></div>
                  <div><p className="text-gray-500">Return Date</p><p className="font-medium">{asset.return_date ? new Date(asset.return_date).toLocaleDateString() : 'Not returned'}</p></div>
                  {asset.notes && <div className="md:col-span-1"><p className="text-gray-500">Notes</p><p className="font-medium truncate">{asset.notes}</p></div>}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500"><Package className="h-12 w-12 mx-auto mb-2 opacity-30" /><p>No assets assigned to this courier</p></div>
        )}
      </CardContent>
    </Card>
  )

  const DocumentsContent = (
    <Card>
      <CardHeader><CardTitle>Documents & IDs</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-2"><h4 className="font-medium">Iqama</h4>{courier.iqama_expiry_date && new Date(courier.iqama_expiry_date) < new Date() ? <Badge variant="danger">Expired</Badge> : <Badge variant="success">Valid</Badge>}</div>
            <p className="text-sm text-gray-500">Number</p><p className="font-medium">{courier.iqama_number || 'N/A'}</p>
            <p className="text-sm text-gray-500 mt-2">Expiry Date</p><p className="font-medium">{courier.iqama_expiry_date ? new Date(courier.iqama_expiry_date).toLocaleDateString() : 'N/A'}</p>
          </div>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-2"><h4 className="font-medium">Passport</h4>{courier.passport_expiry_date && new Date(courier.passport_expiry_date) < new Date() ? <Badge variant="danger">Expired</Badge> : <Badge variant="success">Valid</Badge>}</div>
            <p className="text-sm text-gray-500">Number</p><p className="font-medium">{courier.passport_number || 'N/A'}</p>
            <p className="text-sm text-gray-500 mt-2">Expiry Date</p><p className="font-medium">{courier.passport_expiry_date ? new Date(courier.passport_expiry_date).toLocaleDateString() : 'N/A'}</p>
          </div>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between mb-2"><h4 className="font-medium">Driving License</h4>{courier.license_expiry_date && new Date(courier.license_expiry_date) < new Date() ? <Badge variant="danger">Expired</Badge> : <Badge variant="success">Valid</Badge>}</div>
            <p className="text-sm text-gray-500">Number</p><p className="font-medium">{courier.license_number || 'N/A'}</p>
            <p className="text-sm text-gray-500 mt-2">Type</p><p className="font-medium">{courier.license_type || 'N/A'}</p>
            <p className="text-sm text-gray-500 mt-2">Expiry Date</p><p className="font-medium">{courier.license_expiry_date ? new Date(courier.license_expiry_date).toLocaleDateString() : 'N/A'}</p>
          </div>
          <div className="p-4 border rounded-lg"><h4 className="font-medium mb-2">National ID</h4><p className="text-sm text-gray-500">Number</p><p className="font-medium">{courier.national_id || 'N/A'}</p></div>
          <div className="p-4 border rounded-lg md:col-span-2">
            <h4 className="font-medium mb-2">Platform IDs</h4>
            <div className="grid grid-cols-3 gap-4">
              <div><p className="text-sm text-gray-500">Jahez Driver ID</p><p className="font-medium">{courier.jahez_driver_id || 'N/A'}</p></div>
              <div><p className="text-sm text-gray-500">Hunger Rider ID</p><p className="font-medium">{courier.hunger_rider_id || 'N/A'}</p></div>
              <div><p className="text-sm text-gray-500">Mrsool Courier ID</p><p className="font-medium">{courier.mrsool_courier_id || 'N/A'}</p></div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const BankingContent = (
    <Card>
      <CardHeader><CardTitle>Banking Details</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div><p className="text-sm text-gray-500">Bank Name</p><p className="font-medium">{courier.bank_name || 'N/A'}</p></div>
          <div><p className="text-sm text-gray-500">Account Number</p><p className="font-medium">{courier.bank_account_number || 'N/A'}</p></div>
          <div><p className="text-sm text-gray-500">IBAN</p><p className="font-medium font-mono text-sm">{courier.iban || 'N/A'}</p></div>
        </div>
      </CardContent>
    </Card>
  )

  const AccommodationContent = (
    <Card>
      <CardHeader><CardTitle>Accommodation</CardTitle></CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div><p className="text-sm text-gray-500">Building ID</p><p className="font-medium">{courier.accommodation_building_id || 'Not Assigned'}</p></div>
          <div><p className="text-sm text-gray-500">Room ID</p><p className="font-medium">{courier.accommodation_room_id || 'Not Assigned'}</p></div>
        </div>
        {!courier.accommodation_building_id && (
          <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
            <div className="flex items-center gap-2 text-yellow-800"><AlertTriangle className="h-4 w-4" /><p className="text-sm">No accommodation assigned to this courier</p></div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  // Define tab groups for the new layout system
  const tabGroups: TabGroup[] = [
    {
      id: 'tracking',
      label: 'Tracking & Vehicle',
      icon: <Car className="h-5 w-5 text-white" />,
      color: 'bg-blue-500',
      stats: courierVehicle ? `${courierVehicle.plate_number}` : 'No vehicle',
      tabs: [
        { id: 'live-location', label: 'Live Location', icon: <Radio className="h-4 w-4" />, content: LiveLocationContent },
        { id: 'vehicle', label: 'Vehicle', icon: <Car className="h-4 w-4" />, content: VehicleContent },
        { id: 'vehicle-history', label: 'History', icon: <History className="h-4 w-4" />, content: VehicleHistoryContent, count: courierVehicleHistory.length },
        { id: 'logs', label: 'Logs', icon: <ClipboardList className="h-4 w-4" />, content: LogsContent, count: courierVehicleLogs.length },
      ],
    },
    {
      id: 'hr',
      label: 'HR & Finance',
      icon: <DollarSign className="h-5 w-5 text-white" />,
      color: 'bg-green-500',
      stats: courierSalaries.length > 0 ? `SAR ${courierSalaries[0]?.net_salary?.toLocaleString() || 0} net` : 'No records',
      tabs: [
        { id: 'salaries', label: 'Salaries', icon: <Wallet className="h-4 w-4" />, content: SalariesContent, count: courierSalaries.length },
        { id: 'loans', label: 'Loans', icon: <DollarSign className="h-4 w-4" />, content: LoansContent, count: courierLoans.length },
        { id: 'bonuses', label: 'Bonuses', icon: <Gift className="h-4 w-4" />, content: BonusesContent, count: courierBonuses.length },
        { id: 'leaves', label: 'Leaves', icon: <Clock className="h-4 w-4" />, content: LeavesContent, count: courierLeaves.length },
        { id: 'attendance', label: 'Attendance', icon: <CheckCircle className="h-4 w-4" />, content: AttendanceContent, count: courierAttendance.length },
      ],
    },
    {
      id: 'operations',
      label: 'Operations',
      icon: <Truck className="h-5 w-5 text-white" />,
      color: 'bg-orange-500',
      stats: `${courierDeliveries.length} deliveries`,
      tabs: [
        { id: 'deliveries', label: 'Deliveries', icon: <Truck className="h-4 w-4" />, content: DeliveriesContent, count: courierDeliveries.length },
        { id: 'assets', label: 'Assets', icon: <Package className="h-4 w-4" />, content: AssetsContent, count: courierAssets.length },
      ],
    },
    {
      id: 'info',
      label: 'Info & Documents',
      icon: <FileText className="h-5 w-5 text-white" />,
      color: 'bg-purple-500',
      tabs: [
        { id: 'documents', label: 'Documents', icon: <FileText className="h-4 w-4" />, content: DocumentsContent },
        { id: 'banking', label: 'Banking', icon: <CreditCard className="h-4 w-4" />, content: BankingContent },
        { id: 'accommodation', label: 'Accommodation', icon: <Building className="h-4 w-4" />, content: AccommodationContent },
      ],
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Courier Profile</h1>
          <Badge variant={getStatusBadge(courier.status)} className="text-sm px-3 py-1">
            {courier.status || 'Unknown'}
          </Badge>
        </div>
        <div className="flex items-center gap-3">
          <LayoutSelector currentLayout={layout} onLayoutChange={setLayout} />
        </div>
      </div>

      {/* Profile Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Personal Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div><p className="text-sm text-gray-500">BARQ ID</p><p className="font-medium">{courier.barq_id || 'N/A'}</p></div>
              <div><p className="text-sm text-gray-500">Full Name</p><p className="font-medium">{courier.full_name || 'N/A'}</p></div>
              <div><p className="text-sm text-gray-500">Position</p><p className="font-medium">{courier.position || 'Courier'}</p></div>
              <div className="flex items-start gap-2"><Phone className="h-4 w-4 text-gray-400 mt-1" /><div><p className="text-sm text-gray-500">Phone</p><p className="font-medium">{courier.mobile_number || 'N/A'}</p></div></div>
              <div className="flex items-start gap-2"><Mail className="h-4 w-4 text-gray-400 mt-1" /><div><p className="text-sm text-gray-500">Email</p><p className="font-medium">{courier.email || 'N/A'}</p></div></div>
              <div className="flex items-start gap-2"><MapPin className="h-4 w-4 text-gray-400 mt-1" /><div><p className="text-sm text-gray-500">City</p><p className="font-medium">{courier.city || 'N/A'}</p></div></div>
              <div className="flex items-start gap-2"><Calendar className="h-4 w-4 text-gray-400 mt-1" /><div><p className="text-sm text-gray-500">Joining Date</p><p className="font-medium">{courier.joining_date ? new Date(courier.joining_date).toLocaleDateString() : 'N/A'}</p></div></div>
              <div><p className="text-sm text-gray-500">Nationality</p><p className="font-medium">{courier.nationality || 'N/A'}</p></div>
              <div><p className="text-sm text-gray-500">Sponsorship Status</p><p className="font-medium">{courier.sponsorship_status || 'N/A'}</p></div>
            </div>
          </CardContent>
        </Card>

        {/* Performance Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-3xl font-bold text-blue-600">{courier.performance_score || 0}%</p>
                <p className="text-sm text-gray-500">Performance Score</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-3xl font-bold text-green-600">{courier.total_deliveries || 0}</p>
                <p className="text-sm text-gray-500">Total Deliveries</p>
              </div>
              <div><p className="text-sm text-gray-500">Project Type</p><Badge variant="default" className="mt-1">{courier.project_type || 'N/A'}</Badge></div>
              <div><p className="text-sm text-gray-500">Supervisor</p><p className="font-medium">{courier.supervisor_name || 'N/A'}</p></div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs/Layout for Related Data */}
      <CourierProfileLayout layout={layout} groups={tabGroups} defaultTab="live-location" />

      {/* Notes Section */}
      {courier.notes && (
        <Card>
          <CardHeader><CardTitle>Notes</CardTitle></CardHeader>
          <CardContent><p className="text-gray-700 whitespace-pre-wrap">{courier.notes}</p></CardContent>
        </Card>
      )}

      {/* Emergency Contact */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            Emergency Contact
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div><p className="text-sm text-gray-500">Contact Name</p><p className="font-medium">{courier.emergency_contact_name || 'Not provided'}</p></div>
            <div><p className="text-sm text-gray-500">Contact Phone</p><p className="font-medium">{courier.emergency_contact_phone || 'Not provided'}</p></div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
