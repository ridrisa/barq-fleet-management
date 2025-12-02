import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
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
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { Tabs } from '@/components/ui/Tabs'
import { Table } from '@/components/ui/Table'
import { couriersAPI, vehiclesAPI, leavesAPI, loansAPI, assetsAPI, assignmentsAPI, fmsAPI, salaryAPI, vehicleLogsAPI } from '@/lib/api'

export default function CourierProfile() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

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

  // Define tabs for the Tabs component
  const tabs = [
    {
      id: 'documents',
      label: 'Documents',
      icon: <FileText className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Documents & IDs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Iqama */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Iqama</h4>
                  {courier.iqama_expiry_date && new Date(courier.iqama_expiry_date) < new Date() ? (
                    <Badge variant="danger">Expired</Badge>
                  ) : (
                    <Badge variant="success">Valid</Badge>
                  )}
                </div>
                <p className="text-sm text-gray-500">Number</p>
                <p className="font-medium">{courier.iqama_number || 'N/A'}</p>
                <p className="text-sm text-gray-500 mt-2">Expiry Date</p>
                <p className="font-medium">
                  {courier.iqama_expiry_date
                    ? new Date(courier.iqama_expiry_date).toLocaleDateString()
                    : 'N/A'}
                </p>
              </div>

              {/* Passport */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Passport</h4>
                  {courier.passport_expiry_date && new Date(courier.passport_expiry_date) < new Date() ? (
                    <Badge variant="danger">Expired</Badge>
                  ) : (
                    <Badge variant="success">Valid</Badge>
                  )}
                </div>
                <p className="text-sm text-gray-500">Number</p>
                <p className="font-medium">{courier.passport_number || 'N/A'}</p>
                <p className="text-sm text-gray-500 mt-2">Expiry Date</p>
                <p className="font-medium">
                  {courier.passport_expiry_date
                    ? new Date(courier.passport_expiry_date).toLocaleDateString()
                    : 'N/A'}
                </p>
              </div>

              {/* License */}
              <div className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Driving License</h4>
                  {courier.license_expiry_date && new Date(courier.license_expiry_date) < new Date() ? (
                    <Badge variant="danger">Expired</Badge>
                  ) : (
                    <Badge variant="success">Valid</Badge>
                  )}
                </div>
                <p className="text-sm text-gray-500">Number</p>
                <p className="font-medium">{courier.license_number || 'N/A'}</p>
                <p className="text-sm text-gray-500 mt-2">Type</p>
                <p className="font-medium">{courier.license_type || 'N/A'}</p>
                <p className="text-sm text-gray-500 mt-2">Expiry Date</p>
                <p className="font-medium">
                  {courier.license_expiry_date
                    ? new Date(courier.license_expiry_date).toLocaleDateString()
                    : 'N/A'}
                </p>
              </div>

              {/* National ID */}
              <div className="p-4 border rounded-lg">
                <h4 className="font-medium mb-2">National ID</h4>
                <p className="text-sm text-gray-500">Number</p>
                <p className="font-medium">{courier.national_id || 'N/A'}</p>
              </div>

              {/* Platform IDs */}
              <div className="p-4 border rounded-lg md:col-span-2">
                <h4 className="font-medium mb-2">Platform IDs</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Jahez Driver ID</p>
                    <p className="font-medium">{courier.jahez_driver_id || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Hunger Rider ID</p>
                    <p className="font-medium">{courier.hunger_rider_id || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Mrsool Courier ID</p>
                    <p className="font-medium">{courier.mrsool_courier_id || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'vehicle',
      label: 'Vehicle',
      icon: <Car className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Assigned Vehicle</CardTitle>
          </CardHeader>
          <CardContent>
            {courierVehicle ? (
              <div className="space-y-6">
                {/* Vehicle Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <p className="text-sm text-gray-500">Plate Number</p>
                    <p className="font-medium text-lg">{courierVehicle.plate_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Make & Model</p>
                    <p className="font-medium">
                      {courierVehicle.make} {courierVehicle.model} ({courierVehicle.year})
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <Badge variant={courierVehicle.status === 'active' ? 'success' : 'warning'}>
                      {courierVehicle.status}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Current Mileage</p>
                    <p className="font-medium">{courierVehicle.current_mileage?.toLocaleString() || 0} km</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Vehicle Type</p>
                    <p className="font-medium">{courierVehicle.vehicle_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Color</p>
                    <p className="font-medium">{courierVehicle.color || 'N/A'}</p>
                  </div>
                </div>

                {/* GPS Tracking Info (from FMS/machinettalk) */}
                {fmsVehicle && (
                  <div className="mt-6 pt-6 border-t">
                    <h4 className="font-medium mb-4 flex items-center gap-2">
                      <Navigation className="h-4 w-4 text-blue-600" />
                      Live GPS Tracking
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-gray-500">FMS Asset ID</p>
                        <p className="font-medium">{fmsVehicle.AssetId || fmsVehicle.Id || 'N/A'}</p>
                      </div>
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-xs text-gray-500">GPS Status</p>
                        <p className="font-medium text-green-600">
                          {fmsVehicle.IsOnline ? 'Online' : 'Offline'}
                        </p>
                      </div>
                      <div className="p-3 bg-purple-50 rounded-lg">
                        <p className="text-xs text-gray-500">Current Speed</p>
                        <p className="font-medium">{fmsVehicle.Speed || 0} km/h</p>
                      </div>
                      <div className="p-3 bg-orange-50 rounded-lg">
                        <p className="text-xs text-gray-500">Last Update</p>
                        <p className="font-medium text-sm">
                          {fmsVehicle.LastUpdated
                            ? new Date(fmsVehicle.LastUpdated).toLocaleString()
                            : 'N/A'}
                        </p>
                      </div>
                    </div>
                    {fmsVehicle.Location && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">Last Known Location</p>
                        <p className="font-medium text-sm">
                          Lat: {fmsVehicle.Location.Latitude}, Lng: {fmsVehicle.Location.Longitude}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* GPS Not Available */}
                {!fmsVehicle && courierVehicle.gps_device_id && (
                  <div className="mt-6 pt-6 border-t">
                    <div className="p-4 bg-yellow-50 rounded-lg flex items-center gap-3">
                      <Navigation className="h-5 w-5 text-yellow-600" />
                      <div>
                        <p className="font-medium text-yellow-800">GPS Device Registered</p>
                        <p className="text-sm text-yellow-600">
                          Device ID: {courierVehicle.gps_device_id} - Tracking data not available
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Car className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No vehicle assigned to this courier</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'leaves',
      label: `Leaves (${courierLeaves.length})`,
      icon: <Clock className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Leave History</CardTitle>
          </CardHeader>
          <CardContent>
            {courierLeaves.length > 0 ? (
              <div className="space-y-4">
                {courierLeaves.map((leave: any) => (
                  <div key={leave.id} className="p-4 border rounded-lg flex items-center justify-between">
                    <div>
                      <p className="font-medium">{leave.leave_type || 'Leave'}</p>
                      <p className="text-sm text-gray-500">
                        {leave.start_date ? new Date(leave.start_date).toLocaleDateString() : 'N/A'} -{' '}
                        {leave.end_date ? new Date(leave.end_date).toLocaleDateString() : 'N/A'}
                      </p>
                      <p className="text-sm text-gray-500">{leave.reason || 'No reason provided'}</p>
                    </div>
                    <Badge
                      variant={
                        leave.status === 'approved'
                          ? 'success'
                          : leave.status === 'rejected'
                          ? 'danger'
                          : 'warning'
                      }
                    >
                      {leave.status || 'pending'}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No leave records found</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'loans',
      label: `Loans (${courierLoans.length})`,
      icon: <DollarSign className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Loan History</CardTitle>
          </CardHeader>
          <CardContent>
            {courierLoans.length > 0 ? (
              <>
                {/* Loan Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-blue-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      SAR {courierLoans.reduce((sum: number, l: any) => sum + (Number(l.amount) || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Total Loans</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      SAR {courierLoans.reduce((sum: number, l: any) => sum + (Number(l.outstanding_balance) || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Outstanding Balance</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {courierLoans.filter((l: any) => l.status === 'active').length}
                    </p>
                    <p className="text-sm text-gray-500">Active Loans</p>
                  </div>
                </div>
                {/* Loan List */}
                <div className="space-y-4">
                  {courierLoans.map((loan: any) => (
                    <div key={loan.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="font-medium text-lg">SAR {Number(loan.amount || 0).toLocaleString()}</p>
                          <p className="text-sm text-gray-500">
                            Monthly: SAR {Number(loan.monthly_deduction || 0).toLocaleString()}
                          </p>
                        </div>
                        <Badge
                          variant={
                            loan.status === 'approved' || loan.status === 'paid' || loan.status === 'active'
                              ? 'success'
                              : loan.status === 'rejected'
                              ? 'danger'
                              : 'warning'
                          }
                        >
                          {loan.status || 'pending'}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Start Date</p>
                          <p className="font-medium">{loan.start_date ? new Date(loan.start_date).toLocaleDateString() : 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Outstanding</p>
                          <p className="font-medium">SAR {Number(loan.outstanding_balance || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">End Date</p>
                          <p className="font-medium">{loan.end_date ? new Date(loan.end_date).toLocaleDateString() : 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Reason</p>
                          <p className="font-medium truncate">{loan.reason || 'N/A'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <DollarSign className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No loan records found</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'assets',
      label: `Assets (${courierAssets.length})`,
      icon: <Package className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Assigned Assets</CardTitle>
          </CardHeader>
          <CardContent>
            {courierAssets.length > 0 ? (
              <div className="space-y-4">
                {courierAssets.map((asset: any) => (
                  <div key={asset.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gray-100 rounded-lg">
                          {getAssetIcon(asset.asset_type)}
                        </div>
                        <div>
                          <p className="font-medium capitalize">{asset.asset_type?.replace('_', ' ') || 'Asset'}</p>
                          <p className="text-sm text-gray-500">Issued: {asset.issue_date ? new Date(asset.issue_date).toLocaleDateString() : 'N/A'}</p>
                        </div>
                      </div>
                      <Badge
                        variant={
                          asset.status === 'assigned' ? 'success' :
                          asset.status === 'returned' ? 'default' :
                          asset.status === 'damaged' || asset.status === 'lost' ? 'danger' :
                          'warning'
                        }
                      >
                        {asset.status || 'Unknown'}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Condition</p>
                        <p className="font-medium capitalize">{asset.condition || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Return Date</p>
                        <p className="font-medium">{asset.return_date ? new Date(asset.return_date).toLocaleDateString() : 'Not returned'}</p>
                      </div>
                      {asset.notes && (
                        <div className="md:col-span-1">
                          <p className="text-gray-500">Notes</p>
                          <p className="font-medium truncate">{asset.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Package className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No assets assigned to this courier</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'vehicle-history',
      label: `Vehicle History (${courierVehicleHistory.length})`,
      icon: <History className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Vehicle Assignment History</CardTitle>
          </CardHeader>
          <CardContent>
            {courierVehicleHistory.length > 0 ? (
              <div className="space-y-4">
                {courierVehicleHistory.map((assignment: any) => {
                  const vehicle = vehicles.find((v: any) => v.id === assignment.vehicle_id)
                  return (
                    <div key={assignment.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <Car className="h-5 w-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium">{vehicle?.plate_number || 'Unknown Vehicle'}</p>
                            <p className="text-sm text-gray-500">
                              {vehicle ? `${vehicle.make} ${vehicle.model} (${vehicle.year})` : 'Details not available'}
                            </p>
                          </div>
                        </div>
                        <Badge
                          variant={
                            assignment.status === 'active' ? 'success' :
                            assignment.status === 'completed' ? 'default' :
                            'warning'
                          }
                        >
                          {assignment.status || 'Unknown'}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Start Date</p>
                          <p className="font-medium">{assignment.start_date ? new Date(assignment.start_date).toLocaleDateString() : 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">End Date</p>
                          <p className="font-medium">{assignment.end_date ? new Date(assignment.end_date).toLocaleDateString() : 'Ongoing'}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Start Mileage</p>
                          <p className="font-medium">{assignment.start_mileage?.toLocaleString() || 'N/A'} km</p>
                        </div>
                        <div>
                          <p className="text-gray-500">End Mileage</p>
                          <p className="font-medium">{assignment.end_mileage?.toLocaleString() || 'N/A'} km</p>
                        </div>
                      </div>
                      {assignment.assignment_reason && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-sm text-gray-500">Reason: {assignment.assignment_reason}</p>
                        </div>
                      )}
                      {assignment.termination_reason && (
                        <div className="mt-2">
                          <p className="text-sm text-red-600">Termination: {assignment.termination_reason}</p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <History className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No vehicle assignment history found</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'salaries',
      label: `Salaries (${courierSalaries.length})`,
      icon: <Wallet className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Salary History</CardTitle>
          </CardHeader>
          <CardContent>
            {courierSalaries.length > 0 ? (
              <>
                {/* Salary Summary */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-600">
                      SAR {courierSalaries[0]?.net_salary?.toLocaleString() || 0}
                    </p>
                    <p className="text-sm text-gray-500">Latest Net Salary</p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      SAR {courierSalaries[0]?.gross_salary?.toLocaleString() || 0}
                    </p>
                    <p className="text-sm text-gray-500">Gross Salary</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      SAR {courierSalaries.reduce((sum: number, s: any) => sum + (Number(s.deductions) || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Total Deductions</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-purple-600">{courierSalaries.length}</p>
                    <p className="text-sm text-gray-500">Months Recorded</p>
                  </div>
                </div>
                {/* Salary List */}
                <div className="space-y-4">
                  {courierSalaries.map((salary: any) => (
                    <div key={salary.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="font-medium text-lg">
                            {new Date(salary.year, salary.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                          </p>
                          <p className="text-sm text-gray-500">
                            Payment: {salary.payment_date ? new Date(salary.payment_date).toLocaleDateString() : 'Pending'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-green-600">SAR {Number(salary.net_salary || 0).toLocaleString()}</p>
                          <p className="text-xs text-gray-500">Net Salary</p>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Base Salary</p>
                          <p className="font-medium">SAR {Number(salary.base_salary || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Allowances</p>
                          <p className="font-medium text-green-600">+SAR {Number(salary.allowances || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Deductions</p>
                          <p className="font-medium text-red-600">-SAR {Number(salary.deductions || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Loan Deduction</p>
                          <p className="font-medium text-orange-600">-SAR {Number(salary.loan_deduction || 0).toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">GOSI</p>
                          <p className="font-medium text-purple-600">-SAR {Number(salary.gosi_employee || 0).toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Wallet className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No salary records found</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'vehicle-logs',
      label: `Logs (${courierVehicleLogs.length})`,
      icon: <ClipboardList className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Vehicle Logs & Trips</CardTitle>
          </CardHeader>
          <CardContent>
            {courierVehicleLogs.length > 0 ? (
              <>
                {/* Log Summary */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="p-4 bg-blue-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.distance_covered) || 0), 0).toLocaleString()} km
                    </p>
                    <p className="text-sm text-gray-500">Total Distance</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.number_of_deliveries) || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Total Deliveries</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      SAR {courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.fuel_cost) || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Total Fuel Cost</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      SAR {courierVehicleLogs.reduce((sum: number, l: any) => sum + (Number(l.revenue_generated) || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-sm text-gray-500">Revenue Generated</p>
                  </div>
                </div>
                {/* Log List */}
                <div className="space-y-4">
                  {courierVehicleLogs.slice(0, 10).map((log: any) => {
                    const logVehicle = vehicles.find((v: any) => v.id === log.vehicle_id)
                    return (
                      <div key={log.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${
                              log.log_type === 'fuel_refill' ? 'bg-orange-100' :
                              log.log_type === 'delivery' ? 'bg-green-100' :
                              log.log_type === 'trip' ? 'bg-blue-100' : 'bg-gray-100'
                            }`}>
                              {log.log_type === 'fuel_refill' ? <Fuel className="h-5 w-5 text-orange-600" /> :
                               log.log_type === 'delivery' || log.log_type === 'trip' ? <Route className="h-5 w-5 text-blue-600" /> :
                               <ClipboardList className="h-5 w-5 text-gray-600" />}
                            </div>
                            <div>
                              <p className="font-medium capitalize">{log.log_type?.replace('_', ' ') || 'Daily Log'}</p>
                              <p className="text-sm text-gray-500">
                                {log.log_date ? new Date(log.log_date).toLocaleDateString() : 'N/A'}
                                {logVehicle && ` • ${logVehicle.plate_number}`}
                              </p>
                            </div>
                          </div>
                          <Badge variant={log.has_issues ? 'danger' : 'success'}>
                            {log.vehicle_condition || 'Good'}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">Distance</p>
                            <p className="font-medium">{Number(log.distance_covered || 0).toLocaleString()} km</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Deliveries</p>
                            <p className="font-medium">{log.number_of_deliveries || 0}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Fuel Used</p>
                            <p className="font-medium">{Number(log.fuel_refilled || 0).toLocaleString()} L</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Revenue</p>
                            <p className="font-medium">SAR {Number(log.revenue_generated || 0).toLocaleString()}</p>
                          </div>
                        </div>
                        {log.issues_reported && (
                          <div className="mt-3 pt-3 border-t">
                            <p className="text-sm text-red-600">⚠️ Issues: {log.issues_reported}</p>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
                {courierVehicleLogs.length > 10 && (
                  <div className="mt-4 text-center">
                    <p className="text-sm text-gray-500">Showing 10 of {courierVehicleLogs.length} logs</p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <ClipboardList className="h-12 w-12 mx-auto mb-2 opacity-30" />
                <p>No vehicle logs found for this courier</p>
              </div>
            )}
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'banking',
      label: 'Banking',
      icon: <CreditCard className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Banking Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-500">Bank Name</p>
                <p className="font-medium">{courier.bank_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Account Number</p>
                <p className="font-medium">{courier.bank_account_number || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">IBAN</p>
                <p className="font-medium font-mono text-sm">{courier.iban || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      ),
    },
    {
      id: 'accommodation',
      label: 'Accommodation',
      icon: <Building className="h-4 w-4" />,
      content: (
        <Card>
          <CardHeader>
            <CardTitle>Accommodation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-500">Building ID</p>
                <p className="font-medium">{courier.accommodation_building_id || 'Not Assigned'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Room ID</p>
                <p className="font-medium">{courier.accommodation_room_id || 'Not Assigned'}</p>
              </div>
            </div>
            {!courier.accommodation_building_id && (
              <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
                <div className="flex items-center gap-2 text-yellow-800">
                  <AlertTriangle className="h-4 w-4" />
                  <p className="text-sm">No accommodation assigned to this courier</p>
                </div>
              </div>
            )}
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
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">Courier Profile</h1>
        </div>
        <Badge variant={getStatusBadge(courier.status)} className="text-sm px-3 py-1">
          {courier.status || 'Unknown'}
        </Badge>
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
              <div>
                <p className="text-sm text-gray-500">BARQ ID</p>
                <p className="font-medium">{courier.barq_id || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Full Name</p>
                <p className="font-medium">{courier.full_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Position</p>
                <p className="font-medium">{courier.position || 'Courier'}</p>
              </div>
              <div className="flex items-start gap-2">
                <Phone className="h-4 w-4 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Phone</p>
                  <p className="font-medium">{courier.mobile_number || 'N/A'}</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Mail className="h-4 w-4 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Email</p>
                  <p className="font-medium">{courier.email || 'N/A'}</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">City</p>
                  <p className="font-medium">{courier.city || 'N/A'}</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Calendar className="h-4 w-4 text-gray-400 mt-1" />
                <div>
                  <p className="text-sm text-gray-500">Joining Date</p>
                  <p className="font-medium">
                    {courier.joining_date
                      ? new Date(courier.joining_date).toLocaleDateString()
                      : 'N/A'}
                  </p>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-500">Nationality</p>
                <p className="font-medium">{courier.nationality || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Sponsorship Status</p>
                <p className="font-medium">{courier.sponsorship_status || 'N/A'}</p>
              </div>
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
                <p className="text-3xl font-bold text-blue-600">
                  {courier.performance_score || 0}%
                </p>
                <p className="text-sm text-gray-500">Performance Score</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-3xl font-bold text-green-600">
                  {courier.total_deliveries || 0}
                </p>
                <p className="text-sm text-gray-500">Total Deliveries</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Project Type</p>
                <Badge variant="default" className="mt-1">
                  {courier.project_type || 'N/A'}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-500">Supervisor</p>
                <p className="font-medium">{courier.supervisor_name || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for Related Data */}
      <Tabs tabs={tabs} defaultTab="documents" />

      {/* Notes Section */}
      {courier.notes && (
        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 whitespace-pre-wrap">{courier.notes}</p>
          </CardContent>
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
            <div>
              <p className="text-sm text-gray-500">Contact Name</p>
              <p className="font-medium">{courier.emergency_contact_name || 'Not provided'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Contact Phone</p>
              <p className="font-medium">{courier.emergency_contact_phone || 'Not provided'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
