import { useQuery } from '@tanstack/react-query'
import {
  Users, Truck, Package, TrendingUp, TrendingDown,
  Activity, AlertCircle, CheckCircle, Clock, UserCheck,
  Car, Calendar, AlertTriangle, Bell, Award,
  MapPin, UserPlus, Shield
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  RadialBarChart, RadialBar
} from 'recharts'
import { healthAPI, dashboardAPI } from '@/lib/api'
import { Spinner } from '@/components/ui/Spinner'

// KPI Card Component
function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendValue,
  color = 'blue'
}: {
  title: string
  value: string | number
  subtitle?: string
  icon: any
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'cyan' | 'pink'
}) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
    cyan: 'bg-cyan-100 text-cyan-600',
    pink: 'bg-pink-100 text-pink-600',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && trendValue && (
            <div className={`flex items-center mt-2 text-sm ${
              trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500'
            }`}>
              {trend === 'up' ? <TrendingUp className="w-4 h-4 mr-1" /> :
               trend === 'down' ? <TrendingDown className="w-4 h-4 mr-1" /> : null}
              {trendValue}
            </div>
          )}
        </div>
        <div className={`p-4 rounded-xl ${colorClasses[color]}`}>
          <Icon className="w-8 h-8" />
        </div>
      </div>
    </div>
  )
}

// Progress Bar Component (exported for future use)
export function ProgressBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0
  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{value} / {max}</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

// Alert Card Component
function AlertCard({ alert }: { alert: any }) {
  const typeColors = {
    critical: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  }
  const typeIcons = {
    critical: AlertCircle,
    warning: AlertTriangle,
    info: Bell,
  }
  const Icon = typeIcons[alert.type as keyof typeof typeIcons] || Bell

  return (
    <div className={`p-4 rounded-lg border ${typeColors[alert.type as keyof typeof typeColors]}`}>
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <h4 className="font-medium">{alert.title}</h4>
          <p className="text-sm opacity-80 mt-1">{alert.message}</p>
          <span className="text-xs mt-2 inline-block opacity-70">{alert.action}</span>
        </div>
        <span className="text-lg font-bold">{alert.count}</span>
      </div>
    </div>
  )
}

// Health Score Gauge (exported for future use)
export function HealthScoreGauge({ score, status, color }: { score: number; status: string; color: string }) {
  const data = [{ value: score, fill: color }]

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={200}>
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="60%"
          outerRadius="100%"
          barSize={20}
          data={data}
          startAngle={180}
          endAngle={0}
        >
          <RadialBar
            background
            dataKey="value"
            cornerRadius={10}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold" style={{ color }}>{score}</span>
        <span className="text-sm text-gray-500 capitalize">{status}</span>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data: health, isLoading: isHealthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
  })

  const { data: stats, isLoading: isStatsLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: dashboardAPI.stats,
  })

  const { data: deliveryTrends } = useQuery({
    queryKey: ['deliveryTrends'],
    queryFn: () => dashboardAPI.getChartData('deliveries'),
  })

  const { data: fleetStatus } = useQuery({
    queryKey: ['fleetStatus'],
    queryFn: () => dashboardAPI.getChartData('fleet-status'),
  })

  const { data: alerts } = useQuery({
    queryKey: ['dashboardAlerts'],
    queryFn: dashboardAPI.getAlerts,
  })

  const { data: topCouriers } = useQuery({
    queryKey: ['topCouriers'],
    queryFn: () => dashboardAPI.getTopCouriers(5),
  })

  const { data: recentActivity } = useQuery({
    queryKey: ['recentActivity'],
    queryFn: () => dashboardAPI.getRecentActivity(8),
  })

  const { data: summary } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: dashboardAPI.getSummary,
  })

  const { data: courierStatus } = useQuery({
    queryKey: ['courierStatusChart'],
    queryFn: dashboardAPI.getCourierStatus,
  })

  const { data: cityDistribution } = useQuery({
    queryKey: ['cityDistribution'],
    queryFn: dashboardAPI.getCityDistribution,
  })

  // Sample data for charts when API data is not available
  const sampleTrendData = [
    { day: 'Mon', deliveries: 45, completed: 40, failed: 5 },
    { day: 'Tue', deliveries: 52, completed: 48, failed: 4 },
    { day: 'Wed', deliveries: 49, completed: 45, failed: 4 },
    { day: 'Thu', deliveries: 63, completed: 58, failed: 5 },
    { day: 'Fri', deliveries: 58, completed: 55, failed: 3 },
    { day: 'Sat', deliveries: 48, completed: 44, failed: 4 },
    { day: 'Sun', deliveries: 38, completed: 35, failed: 3 },
  ]

  const pieData = fleetStatus?.fleet_status || [
    { name: 'Available', value: stats?.vehicles_available || 5, color: '#10B981' },
    { name: 'Assigned', value: stats?.vehicles_assigned || 3, color: '#3B82F6' },
    { name: 'Maintenance', value: stats?.vehicles_maintenance || 2, color: '#F59E0B' },
  ]

  const courierStatusData = courierStatus?.courier_status || [
    { name: 'Active', value: stats?.active_couriers || 8, color: '#10B981' },
    { name: 'On Leave', value: stats?.on_leave_couriers || 2, color: '#3B82F6' },
    { name: 'Onboarding', value: stats?.onboarding_couriers || 1, color: '#8B5CF6' },
  ]

  if (isStatsLoading || isHealthLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome to BARQ Fleet Management</p>
        </div>
        <div className="flex items-center space-x-3">
          {alerts?.summary?.critical > 0 && (
            <div className="flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-red-100 text-red-700">
              <AlertCircle className="w-4 h-4 mr-1.5" />
              {alerts.summary.critical} Critical
            </div>
          )}
          <div className={`flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${
            health?.status === 'healthy'
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}>
            {health?.status === 'healthy' ? (
              <CheckCircle className="w-4 h-4 mr-1.5" />
            ) : (
              <AlertCircle className="w-4 h-4 mr-1.5" />
            )}
            System {health?.status || 'checking...'}
          </div>
        </div>
      </div>

      {/* Fleet Health Score Card */}
      {summary?.health_score && (
        <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl p-6 text-white">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-center">
            <div className="lg:col-span-1">
              <h3 className="text-lg font-medium opacity-90">Fleet Health Score</h3>
              <div className="mt-2 flex items-baseline">
                <span className="text-5xl font-bold">{summary.health_score.overall_score}</span>
                <span className="text-2xl ml-1">/100</span>
              </div>
              <p className="mt-2 text-sm opacity-80 capitalize">{summary.health_score.status}</p>
            </div>
            <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
              {summary.health_score.breakdown?.map((item: any, index: number) => (
                <div key={index} className="bg-white/10 rounded-lg p-4">
                  <p className="text-sm opacity-80">{item.name}</p>
                  <p className="text-2xl font-bold mt-1">{item.score}%</p>
                  <p className="text-xs opacity-60 mt-1">Weight: {item.weight}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* KPI Cards - Row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Couriers"
          value={stats?.total_couriers || 0}
          subtitle={`${stats?.active_couriers || 0} active`}
          icon={Users}
          trend={stats?.courier_growth_rate > 0 ? 'up' : stats?.courier_growth_rate < 0 ? 'down' : 'neutral'}
          trendValue={`${stats?.courier_growth_rate > 0 ? '+' : ''}${stats?.courier_growth_rate || 0}% this week`}
          color="blue"
        />
        <KPICard
          title="Total Vehicles"
          value={stats?.total_vehicles || 0}
          subtitle={`${stats?.vehicles_available || 0} available`}
          icon={Truck}
          color="green"
        />
        <KPICard
          title="Active Assignments"
          value={stats?.total_assignments || 0}
          subtitle={`+${stats?.new_assignments_this_week || 0} this week`}
          icon={Package}
          trend="up"
          trendValue="Active operations"
          color="purple"
        />
        <KPICard
          title="Fleet Utilization"
          value={`${stats?.vehicle_utilization || 0}%`}
          subtitle="Vehicles in use"
          icon={Activity}
          trend={stats?.vehicle_utilization > 50 ? 'up' : 'down'}
          trendValue={stats?.vehicle_utilization > 50 ? 'Good utilization' : 'Needs attention'}
          color={stats?.vehicle_utilization > 50 ? 'green' : 'orange'}
        />
      </div>

      {/* KPI Cards - Row 2: Courier Status */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <UserCheck className="w-5 h-5 text-green-600" />
            <span className="text-2xl font-bold text-green-600">{stats?.active_couriers || 0}</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">Active</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <Clock className="w-5 h-5 text-gray-600" />
            <span className="text-2xl font-bold text-gray-600">{stats?.inactive_couriers || 0}</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">Inactive</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <Calendar className="w-5 h-5 text-blue-600" />
            <span className="text-2xl font-bold text-blue-600">{stats?.on_leave_couriers || 0}</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">On Leave</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <UserPlus className="w-5 h-5 text-purple-600" />
            <span className="text-2xl font-bold text-purple-600">{stats?.onboarding_couriers || 0}</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">Onboarding</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span className="text-2xl font-bold text-red-600">{stats?.suspended_couriers || 0}</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">Suspended</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <Car className="w-5 h-5 text-cyan-600" />
            <span className="text-2xl font-bold text-cyan-600">{stats?.couriers_with_vehicle || 0}</span>
          </div>
          <p className="text-sm text-gray-500 mt-2">With Vehicle</p>
        </div>
      </div>

      {/* Alerts Section */}
      {alerts?.alerts && alerts.alerts.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Alerts & Notifications</h3>
            <div className="flex items-center gap-3 text-sm">
              {alerts.summary?.critical > 0 && (
                <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full">
                  {alerts.summary.critical} Critical
                </span>
              )}
              {alerts.summary?.warning > 0 && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full">
                  {alerts.summary.warning} Warning
                </span>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {alerts.alerts.slice(0, 6).map((alert: any, index: number) => (
              <AlertCard key={index} alert={alert} />
            ))}
          </div>
        </div>
      )}

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Delivery Trends Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Activity Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={deliveryTrends?.trend_data || sampleTrendData}>
              <defs>
                <linearGradient id="colorDeliveries" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="day" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="deliveries"
                stroke="#3B82F6"
                fillOpacity={1}
                fill="url(#colorDeliveries)"
                name="Total Tasks"
              />
              <Area
                type="monotone"
                dataKey="completed"
                stroke="#10B981"
                fillOpacity={1}
                fill="url(#colorCompleted)"
                name="Completed"
              />
              <Area
                type="monotone"
                dataKey="failed"
                stroke="#EF4444"
                fillOpacity={1}
                fill="url(#colorFailed)"
                name="Failed"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Fleet Status Pie Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Fleet Status</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-3 mt-2">
            {pieData.map((item: any, index: number) => (
              <div key={index} className="flex items-center">
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-gray-600">{item.name}: {item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Courier Status Distribution */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Courier Status Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={courierStatusData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
              <YAxis dataKey="name" type="category" stroke="#9CA3AF" fontSize={12} width={80} />
              <Tooltip />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {courierStatusData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* City Distribution */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Couriers by City</h3>
          {cityDistribution?.city_distribution && cityDistribution.city_distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={cityDistribution.city_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="name" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {cityDistribution.city_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[250px] text-gray-500">
              <div className="text-center">
                <MapPin className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No city data available</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Couriers */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Top Performers</h3>
            <Award className="w-5 h-5 text-yellow-500" />
          </div>
          {topCouriers?.top_couriers && topCouriers.top_couriers.length > 0 ? (
            <div className="space-y-3">
              {topCouriers.top_couriers.map((courier: any) => (
                <div key={courier.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      courier.rank === 1 ? 'bg-yellow-500' :
                      courier.rank === 2 ? 'bg-gray-400' :
                      courier.rank === 3 ? 'bg-amber-600' :
                      'bg-gray-300'
                    }`}>
                      {courier.rank}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{courier.name}</p>
                      <p className="text-xs text-gray-500">{courier.barq_id}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-blue-600">{courier.performance_score}</p>
                    <p className="text-xs text-gray-500">{courier.total_deliveries} deliveries</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              <p>No performance data yet</p>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          {recentActivity?.activities && recentActivity.activities.length > 0 ? (
            <div className="space-y-3">
              {recentActivity.activities.slice(0, 6).map((activity: any, index: number) => (
                <div key={index} className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    activity.color === 'green' ? 'bg-green-100 text-green-600' :
                    activity.color === 'blue' ? 'bg-blue-100 text-blue-600' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {activity.type === 'new_courier' ? <UserPlus className="w-4 h-4" /> :
                     activity.type === 'assignment' ? <Truck className="w-4 h-4" /> :
                     <Activity className="w-4 h-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                    <p className="text-xs text-gray-500 truncate">{activity.description}</p>
                  </div>
                  {activity.timestamp && (
                    <span className="text-xs text-gray-400">
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              <p>No recent activity</p>
            </div>
          )}
        </div>

        {/* System Health & Quick Stats */}
        <div className="space-y-6">
          {/* System Health */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">API Status</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  health?.status === 'healthy'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  {health?.status || 'Unknown'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Database</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  health?.checks?.database?.status === 'healthy'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {health?.checks?.database?.status || 'Connected'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Version</span>
                <span className="text-gray-900 font-medium">{health?.version || '1.0.0'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Environment</span>
                <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                  {health?.environment || 'development'}
                </span>
              </div>
            </div>
          </div>

          {/* Sponsorship Breakdown */}
          {stats?.sponsorship_breakdown && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sponsorship Type</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 bg-blue-50 rounded-lg">
                  <span className="text-gray-700">Ajeer</span>
                  <span className="font-semibold text-blue-600">{stats.sponsorship_breakdown.ajeer}</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-green-50 rounded-lg">
                  <span className="text-gray-700">In-house</span>
                  <span className="font-semibold text-green-600">{stats.sponsorship_breakdown.inhouse}</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-orange-50 rounded-lg">
                  <span className="text-gray-700">Freelancer</span>
                  <span className="font-semibold text-orange-600">{stats.sponsorship_breakdown.freelancer}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Insights Banner */}
      {stats?.insights && (
        <div className={`rounded-xl p-6 ${
          stats.insights.fleet_health === 'good'
            ? 'bg-gradient-to-r from-green-500 to-emerald-600'
            : 'bg-gradient-to-r from-orange-500 to-amber-600'
        }`}>
          <div className="flex items-center justify-between text-white">
            <div>
              <h3 className="text-xl font-semibold">Fleet Insights</h3>
              <p className="mt-1 opacity-90">
                {stats.insights.fleet_health === 'good'
                  ? 'Your fleet is operating efficiently with good vehicle utilization.'
                  : 'Consider optimizing vehicle assignments to improve utilization.'}
              </p>
              <div className="mt-3 flex items-center gap-4 text-sm opacity-80">
                <span className="flex items-center gap-1">
                  <Shield className="w-4 h-4" />
                  Coverage: {stats.insights.vehicle_coverage}
                </span>
                <span className="flex items-center gap-1">
                  <TrendingUp className="w-4 h-4" />
                  Trend: {stats.insights.growth_trend}
                </span>
                <span className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  Availability: {stats.insights.courier_availability}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold">{stats.vehicle_utilization}%</div>
              <div className="text-sm opacity-90">Fleet Utilization</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
