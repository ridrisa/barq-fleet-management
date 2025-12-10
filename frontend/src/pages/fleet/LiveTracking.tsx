import { useState, useEffect, useCallback, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  MapPin,
  Navigation,
  RefreshCw,
  Users,
  Truck,
  Activity,
  Wifi,
  WifiOff,
  Search,
  Settings,
  Maximize2,
  ChevronRight,
  Clock,
  Gauge,
} from 'lucide-react'
import { fmsAPI, fmsSyncAPI } from '../../lib/api'

// Types
interface Position {
  latitude: number
  longitude: number
  altitude?: number
  direction?: number
}

interface CourierLocation {
  courier_id?: number
  courier_name?: string
  barq_id: string
  fms_asset_id: number
  asset_name?: string
  driver_name?: string
  position: Position
  speed_kmh: number
  mileage_km?: number
  gps_timestamp?: string
  status?: string
  signal_strength?: number
}

interface SyncStats {
  couriers: {
    total: number
    linked_to_fms: number
    unlinked: number
    link_percentage: number
  }
  vehicles: {
    total: number
    linked_to_fms: number
    unlinked: number
    link_percentage: number
  }
  fms: {
    total_assets: number
  }
}

interface FleetSummary {
  total: number
  active: number
  idle: number
  offline: number
  moving: number
  stationary: number
  avg_speed_kmh: number
}

// Custom marker icons
const createCustomIcon = (color: string, isMoving: boolean) => {
  const iconHtml = `
    <div style="
      background: ${color};
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid white;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
      ${isMoving ? 'animation: pulse 2s infinite;' : ''}
    ">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
        ${isMoving
          ? '<path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/>' // Navigation arrow
          : '<circle cx="12" cy="12" r="6"/>' // Static dot
        }
      </svg>
    </div>
  `

  return L.divIcon({
    html: iconHtml,
    className: 'custom-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  })
}

// Map component to update view
function MapUpdater({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap()

  useEffect(() => {
    if (center[0] !== 0 && center[1] !== 0) {
      map.setView(center, zoom, { animate: true })
    }
  }, [center, zoom, map])

  return null
}

// Add CSS animation styles
const animationStyles = `
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
  }

  .custom-marker {
    background: transparent;
    border: none;
  }

  .leaflet-popup-content-wrapper {
    border-radius: 12px;
    padding: 0;
  }

  .leaflet-popup-content {
    margin: 0;
    min-width: 240px;
  }
`

export default function LiveTracking() {
  const [locations, setLocations] = useState<CourierLocation[]>([])
  const [summary, setSummary] = useState<FleetSummary | null>(null)
  const [syncStats, setSyncStats] = useState<SyncStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(30) // seconds
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCourier, setSelectedCourier] = useState<CourierLocation | null>(null)
  const [showSidebar, setShowSidebar] = useState(true)
  const [statusFilter, setStatusFilter] = useState<'all' | 'moving' | 'idle'>('all')

  // Default center (Riyadh, Saudi Arabia)
  const [mapCenter, setMapCenter] = useState<[number, number]>([24.7136, 46.6753])
  const [mapZoom, setMapZoom] = useState(11)

  // Fetch locations
  const fetchLocations = useCallback(async () => {
    try {
      const response = await fmsSyncAPI.getLiveLocations()

      const fetchedLocations = response.locations || []
      setLocations(fetchedLocations)
      setLastUpdate(new Date())

      // Auto-center map on first load if we have locations
      if (fetchedLocations.length > 0 && !lastUpdate) {
        const validLocations = fetchedLocations.filter(
          (loc: CourierLocation) => loc.position.latitude && loc.position.longitude
        )
        if (validLocations.length > 0) {
          // Center on first valid location
          setMapCenter([validLocations[0].position.latitude, validLocations[0].position.longitude])
        }
      }
    } catch (error) {
      console.error('Error fetching locations:', error)
    } finally {
      setLoading(false)
    }
  }, [lastUpdate])

  // Fetch fleet summary
  const fetchSummary = useCallback(async () => {
    try {
      const data = await fmsAPI.getFleetSummary()
      setSummary(data)
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }, [])

  // Fetch sync stats
  const fetchSyncStats = useCallback(async () => {
    try {
      const data = await fmsSyncAPI.getStats()
      setSyncStats(data)
    } catch (error) {
      console.error('Error fetching sync stats:', error)
    }
  }, [])

  // Run FMS sync
  const runSync = async () => {
    setSyncing(true)
    try {
      await fmsSyncAPI.runSync()
      // Refresh data after sync
      await Promise.all([fetchLocations(), fetchSyncStats()])
    } catch (error) {
      console.error('Error running sync:', error)
    } finally {
      setSyncing(false)
    }
  }

  // Initial load and auto-refresh
  useEffect(() => {
    fetchLocations()
    fetchSummary()
    fetchSyncStats()

    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchLocations()
        fetchSummary()
      }, refreshInterval * 1000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval, fetchLocations, fetchSummary, fetchSyncStats])

  // Filter locations
  const filteredLocations = useMemo(() => {
    return locations.filter(loc => {
      // Search filter
      const searchMatch = searchQuery === '' ||
        loc.barq_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        loc.courier_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        loc.driver_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        loc.asset_name?.toLowerCase().includes(searchQuery.toLowerCase())

      // Status filter
      const isMoving = loc.speed_kmh > 5
      const statusMatch = statusFilter === 'all' ||
        (statusFilter === 'moving' && isMoving) ||
        (statusFilter === 'idle' && !isMoving)

      return searchMatch && statusMatch
    })
  }, [locations, searchQuery, statusFilter])

  // Get marker color based on status
  const getMarkerColor = (location: CourierLocation) => {
    if (location.speed_kmh > 5) return '#22c55e' // Green - moving
    if (location.status === 'offline') return '#ef4444' // Red - offline
    return '#f59e0b' // Yellow - idle
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Add animation styles */}
      <style>{animationStyles}</style>

      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <MapPin className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-semibold text-gray-900">Live Fleet Tracking</h1>
            </div>

            {/* Status badges */}
            {summary && (
              <div className="flex items-center gap-2 ml-4">
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                  <Activity className="w-3 h-3" />
                  {summary.moving} Moving
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded-full">
                  <Clock className="w-3 h-3" />
                  {summary.idle} Idle
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
                  <WifiOff className="w-3 h-3" />
                  {summary.offline} Offline
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Auto-refresh toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  autoRefresh
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {autoRefresh ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
                {autoRefresh ? 'Auto' : 'Manual'}
              </button>

              {autoRefresh && (
                <select
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(Number(e.target.value))}
                  className="px-2 py-1.5 text-sm border rounded-lg bg-white"
                >
                  <option value={10}>10s</option>
                  <option value={30}>30s</option>
                  <option value={60}>1m</option>
                </select>
              )}
            </div>

            {/* Last update */}
            {lastUpdate && (
              <span className="text-xs text-gray-500">
                Updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}

            {/* Manual refresh */}
            <button
              onClick={() => {
                fetchLocations()
                fetchSummary()
              }}
              disabled={loading}
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>

            {/* Sync button */}
            <button
              onClick={runSync}
              disabled={syncing}
              className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50"
            >
              <Settings className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
              Sync FMS
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        {showSidebar && (
          <div className="w-80 bg-white border-r flex flex-col">
            {/* Search and filter */}
            <div className="p-4 border-b space-y-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search couriers..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-1">
                {(['all', 'moving', 'idle'] as const).map((status) => (
                  <button
                    key={status}
                    onClick={() => setStatusFilter(status)}
                    className={`flex-1 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                      statusFilter === status
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Sync stats */}
            {syncStats && (
              <div className="p-4 border-b bg-gray-50">
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">FMS Sync Status</h3>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-blue-600" />
                    <span>{syncStats.couriers.linked_to_fms}/{syncStats.couriers.total} linked</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Truck className="w-4 h-4 text-green-600" />
                    <span>{syncStats.vehicles.linked_to_fms}/{syncStats.vehicles.total} linked</span>
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  FMS Assets: {syncStats.fms.total_assets}
                </div>
              </div>
            )}

            {/* Courier list */}
            <div className="flex-1 overflow-y-auto">
              {filteredLocations.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <MapPin className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p className="font-medium">No couriers found</p>
                  <p className="text-sm mt-1">Try adjusting your filters or run FMS sync</p>
                </div>
              ) : (
                <div className="divide-y">
                  {filteredLocations.map((location) => (
                    <button
                      key={location.fms_asset_id}
                      onClick={() => {
                        setSelectedCourier(location)
                        setMapCenter([location.position.latitude, location.position.longitude])
                        setMapZoom(15)
                      }}
                      className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                        selectedCourier?.fms_asset_id === location.fms_asset_id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: getMarkerColor(location) }}
                            />
                            <span className="font-medium text-gray-900 truncate">
                              {location.courier_name || location.driver_name || 'Unknown'}
                            </span>
                          </div>
                          <div className="mt-1 text-xs text-gray-500 space-y-0.5">
                            <div>BARQ ID: {location.barq_id}</div>
                            {location.asset_name && <div>Vehicle: {location.asset_name}</div>}
                          </div>
                        </div>

                        <div className="flex flex-col items-end gap-1 ml-2">
                          <span className={`inline-flex items-center gap-1 text-xs font-medium ${
                            location.speed_kmh > 5 ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            <Gauge className="w-3 h-3" />
                            {location.speed_kmh.toFixed(0)} km/h
                          </span>
                          <ChevronRight className="w-4 h-4 text-gray-400" />
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Sidebar footer */}
            <div className="p-4 border-t bg-gray-50 text-center text-xs text-gray-500">
              Showing {filteredLocations.length} of {locations.length} couriers
            </div>
          </div>
        )}

        {/* Map container */}
        <div className="flex-1 relative">
          {/* Toggle sidebar button */}
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="absolute top-4 left-4 z-[1000] p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50"
          >
            <ChevronRight className={`w-5 h-5 transition-transform ${showSidebar ? 'rotate-180' : ''}`} />
          </button>

          {/* Full screen button */}
          <button
            onClick={() => {
              const elem = document.documentElement
              if (elem.requestFullscreen) {
                elem.requestFullscreen()
              }
            }}
            className="absolute top-4 right-4 z-[1000] p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50"
          >
            <Maximize2 className="w-5 h-5" />
          </button>

          {/* Summary overlay */}
          {summary && (
            <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-gray-900">{summary.total}</div>
                  <div className="text-xs text-gray-500">Total Assets</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-600">{summary.active}</div>
                  <div className="text-xs text-gray-500">Active</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {summary.avg_speed_kmh.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">Avg Speed</div>
                </div>
              </div>
            </div>
          )}

          {/* Loading overlay */}
          {loading && locations.length === 0 && (
            <div className="absolute inset-0 z-[1001] bg-white/80 flex items-center justify-center">
              <div className="text-center">
                <RefreshCw className="w-10 h-10 animate-spin text-blue-600 mx-auto mb-3" />
                <p className="text-gray-600 font-medium">Loading fleet data...</p>
              </div>
            </div>
          )}

          {/* Map */}
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            className="h-full w-full"
            scrollWheelZoom={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapUpdater center={mapCenter} zoom={mapZoom} />

            {filteredLocations.map((location) => (
              <Marker
                key={location.fms_asset_id}
                position={[location.position.latitude, location.position.longitude]}
                icon={createCustomIcon(getMarkerColor(location), location.speed_kmh > 5)}
                eventHandlers={{
                  click: () => setSelectedCourier(location)
                }}
              >
                <Popup>
                  <div className="min-w-[200px]">
                    <div className="font-semibold text-gray-900 mb-2 pb-2 border-b">
                      {location.courier_name || location.driver_name || 'Unknown Driver'}
                    </div>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">BARQ ID:</span>
                        <span className="font-medium">{location.barq_id}</span>
                      </div>
                      {location.asset_name && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Vehicle:</span>
                          <span className="font-medium">{location.asset_name}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-gray-500">Speed:</span>
                        <span className={`font-medium ${location.speed_kmh > 5 ? 'text-green-600' : 'text-yellow-600'}`}>
                          {location.speed_kmh.toFixed(1)} km/h
                        </span>
                      </div>
                      {location.mileage_km && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Mileage:</span>
                          <span className="font-medium">{location.mileage_km.toFixed(0)} km</span>
                        </div>
                      )}
                      {location.gps_timestamp && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Last Update:</span>
                          <span className="font-medium text-xs">
                            {new Date(location.gps_timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="mt-3 pt-2 border-t">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        location.speed_kmh > 5
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {location.speed_kmh > 5 ? (
                          <>
                            <Navigation className="w-3 h-3" />
                            Moving
                          </>
                        ) : (
                          <>
                            <Clock className="w-3 h-3" />
                            Idle
                          </>
                        )}
                      </span>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}
