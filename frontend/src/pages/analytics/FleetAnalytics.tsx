import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Truck, Settings, Fuel, TrendingUp, Download } from 'lucide-react'
import { KPICard, LineChart, BarChart, PieChart, AreaChart, Select, DateRangePicker, Button, Card, CardContent, Table, Spinner } from '@/components/ui'
import { vehiclesAPI, maintenanceAPI, fuelTrackingAPI } from '@/lib/api'

export default function FleetAnalytics() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [vehicleType, setVehicleType] = useState('all')
  const [vehicleStatus, setVehicleStatus] = useState('all')

  // Fetch vehicle data
  const { data: vehicles, isLoading: vehiclesLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesAPI.getAll(),
  })

  // Fetch maintenance data
  const { data: _upcomingMaintenance } = useQuery({
    queryKey: ['maintenance-upcoming'],
    queryFn: () => maintenanceAPI.getUpcoming(30),
  })

  // Fetch fuel tracking summary
  const { data: _fuelSummary } = useQuery({
    queryKey: ['fuel-summary', dateRange],
    queryFn: () => fuelTrackingAPI.getSummary(dateRange.start, dateRange.end),
  })

  // Mock data for charts (in production, these would come from API)
  const vehicleUsageData = [
    { date: '2024-01-01', utilization: 84 },
    { date: '2024-01-02', utilization: 86 },
    { date: '2024-01-03', utilization: 83 },
    { date: '2024-01-04', utilization: 88 },
    { date: '2024-01-05', utilization: 87 },
    { date: '2024-01-06', utilization: 85 },
    { date: '2024-01-07', utilization: 89 },
  ]

  const maintenanceCostData = [
    { vehicle: 'VEH-001', cost: 4500 },
    { vehicle: 'VEH-002', cost: 3200 },
    { vehicle: 'VEH-003', cost: 5800 },
    { vehicle: 'VEH-004', cost: 2900 },
    { vehicle: 'VEH-005', cost: 6200 },
  ]

  const fuelConsumptionData = [
    { date: '2024-01-01', consumption: 425 },
    { date: '2024-01-02', consumption: 438 },
    { date: '2024-01-03', consumption: 412 },
    { date: '2024-01-04', consumption: 445 },
    { date: '2024-01-05', consumption: 451 },
    { date: '2024-01-06', consumption: 429 },
    { date: '2024-01-07', consumption: 456 },
  ]

  const vehicleStatusData = [
    { name: 'Active', value: 48, color: '#10b981' },
    { name: 'Idle', value: 14, color: '#f59e0b' },
    { name: 'Maintenance', value: 6, color: '#ef4444' },
  ]

  const topVehiclesByUtilization = [
    { vehicle: 'VEH-012', type: 'Van', utilization: 96, distance: 2450 },
    { vehicle: 'VEH-034', type: 'Motorcycle', utilization: 94, distance: 1890 },
    { vehicle: 'VEH-007', type: 'SUV', utilization: 92, distance: 2210 },
    { vehicle: 'VEH-021', type: 'Sedan', utilization: 91, distance: 2080 },
    { vehicle: 'VEH-045', type: 'Van', utilization: 89, distance: 2350 },
  ]

  const maintenanceSchedule = [
    { vehicle: 'VEH-003', nextService: '2024-01-15', type: 'Oil Change', priority: 'High' },
    { vehicle: 'VEH-018', nextService: '2024-01-18', type: 'Tire Rotation', priority: 'Medium' },
    { vehicle: 'VEH-029', nextService: '2024-01-20', type: 'Brake Check', priority: 'High' },
    { vehicle: 'VEH-042', nextService: '2024-01-25', type: 'General Service', priority: 'Low' },
  ]

  const fuelEfficiency = [
    { vehicle: 'VEH-012', efficiency: 8.2, fuel: 'Diesel' },
    { vehicle: 'VEH-034', efficiency: 3.5, fuel: 'Petrol' },
    { vehicle: 'VEH-007', efficiency: 11.5, fuel: 'Diesel' },
    { vehicle: 'VEH-021', efficiency: 7.8, fuel: 'Petrol' },
    { vehicle: 'VEH-045', efficiency: 9.1, fuel: 'Diesel' },
  ]

  // Calculate KPI values
  const totalVehicles = vehicles?.length || 68
  const activeVehicles = vehicles?.filter((v: any) => v.status === 'active').length || 48
  const underMaintenance = vehicles?.filter((v: any) => v.status === 'maintenance').length || 6
  const utilizationRate = totalVehicles > 0 ? ((activeVehicles / totalVehicles) * 100).toFixed(1) : '0.0'

  const handleExport = () => {
    console.log('Exporting fleet analytics data...')
    // TODO: Implement export functionality
  }

  if (vehiclesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Fleet Analytics</h1>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Select
            value={vehicleType}
            onChange={(e) => setVehicleType(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="sedan">Sedan</option>
            <option value="suv">SUV</option>
            <option value="van">Van</option>
            <option value="motorcycle">Motorcycle</option>
          </Select>
          <Select
            value={vehicleStatus}
            onChange={(e) => setVehicleStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="idle">Idle</option>
            <option value="maintenance">Maintenance</option>
          </Select>
          <DateRangePicker
            startDate={dateRange.start}
            endDate={dateRange.end}
            onRangeChange={(start, end) => setDateRange({ start, end })}
          />
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Vehicles"
          value={totalVehicles.toString()}
          change={0}
          trend="up"
          icon={<Truck className="w-6 h-6" />}
          color="blue"
        />
        <KPICard
          title="Active Vehicles"
          value={activeVehicles.toString()}
          change={6.7}
          trend="up"
          icon={<TrendingUp className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Under Maintenance"
          value={underMaintenance.toString()}
          change={-12.5}
          trend="down"
          icon={<Settings className="w-6 h-6" />}
          color="yellow"
        />
        <KPICard
          title="Utilization Rate"
          value={`${utilizationRate}%`}
          change={3.2}
          trend="up"
          icon={<Fuel className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={vehicleUsageData}
          xKey="date"
          yKey="utilization"
          title="Vehicle Utilization Trend (Last 30 Days)"
          height={300}
          formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          formatYAxis={(value) => `${value}%`}
        />

        <BarChart
          data={maintenanceCostData}
          xKey="vehicle"
          yKey="cost"
          title="Maintenance Cost by Vehicle"
          height={300}
          formatYAxis={(value) => `${value} SAR`}
        />

        <AreaChart
          data={fuelConsumptionData}
          xKey="date"
          yKey="consumption"
          title="Fuel Consumption Trend"
          height={300}
          formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          formatYAxis={(value) => `${value}L`}
        />

        <PieChart
          data={vehicleStatusData}
          dataKey="value"
          nameKey="name"
          title="Vehicle Status Distribution"
          height={300}
          colors={vehicleStatusData.map(d => d.color)}
        />
      </div>

      {/* Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Top 5 Vehicles by Utilization</h3>
            <Table
              data={topVehiclesByUtilization}
              columns={[
                { key: 'vehicle', header: 'Vehicle', sortable: true },
                { key: 'type', header: 'Type' },
                { key: 'utilization', header: 'Utilization', render: (row: any) => `${row.utilization}%` },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Vehicles Needing Maintenance Soon</h3>
            <Table
              data={maintenanceSchedule}
              columns={[
                { key: 'vehicle', header: 'Vehicle', sortable: true },
                { key: 'nextService', header: 'Next Service' },
                { key: 'type', header: 'Type' },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Fuel Efficiency Ranking</h3>
            <Table
              data={fuelEfficiency}
              columns={[
                { key: 'vehicle', header: 'Vehicle', sortable: true },
                { key: 'efficiency', header: 'L/100km' },
                { key: 'fuel', header: 'Fuel Type' },
              ]}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
