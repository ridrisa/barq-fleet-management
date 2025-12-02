
export const VEHICLE_TYPES = ['sedan', 'van', 'truck', 'motorcycle', 'bicycle'] as const
export const VEHICLE_FUEL_TYPES = ['gasoline', 'diesel', 'electric', 'hybrid'] as const
export const VEHICLE_OWNERSHIP = ['owned', 'leased', 'rented'] as const
export const VEHICLE_STATUSES = ['available', 'in_use', 'maintenance', 'retired'] as const

export type VehicleType = (typeof VEHICLE_TYPES)[number]
export type VehicleFuelType = (typeof VEHICLE_FUEL_TYPES)[number]
export type VehicleOwnership = (typeof VEHICLE_OWNERSHIP)[number]
export type VehicleStatus = (typeof VEHICLE_STATUSES)[number]
export type VehicleId = number

export interface Vehicle {
  id: VehicleId
  plate_number: string
  type: VehicleType
  vehicle_type?: string | null
  make: string
  model: string
  year: number
  color?: string | null
  fuel_type: VehicleFuelType
  ownership: VehicleOwnership
  status: VehicleStatus
  mileage?: number | null
  current_mileage?: number | null
  vin?: string | null
  purchase_date?: string | null
  registration_expiry?: string | null
  insurance_expiry?: string | null
  last_maintenance?: string | null
  assigned_courier_id?: number | null
  assigned_to_city?: string | null
  gps_device_id?: string | null
  created_at?: string
  updated_at?: string
}
