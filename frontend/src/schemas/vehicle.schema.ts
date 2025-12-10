import { z } from 'zod'
import {
  VEHICLE_TYPES,
  VEHICLE_FUEL_TYPES,
  VEHICLE_OWNERSHIP,
  VEHICLE_STATUSES,
} from '@/types/fleet'

/**
 * Vehicle type enum schema
 */
export const vehicleTypeSchema = z.enum(VEHICLE_TYPES)

/**
 * Fuel type enum schema
 */
export const fuelTypeSchema = z.enum(VEHICLE_FUEL_TYPES)

/**
 * Ownership type enum schema
 */
export const ownershipSchema = z.enum(VEHICLE_OWNERSHIP)

/**
 * Vehicle status enum schema
 */
export const vehicleStatusSchema = z.enum(VEHICLE_STATUSES)

/**
 * Plate number validation (Saudi/UAE format)
 * Examples: ABC 1234, 1234 ABC, ABC-1234
 */
const plateNumberRegex = /^[A-Za-z0-9\s\-]{3,15}$/

/**
 * VIN (Vehicle Identification Number) validation
 * 17 characters, alphanumeric excluding I, O, Q
 */
const vinRegex = /^[A-HJ-NPR-Z0-9]{17}$/i

/**
 * Vehicle form validation schema
 */
export const vehicleSchema = z.object({
  plate_number: z
    .string()
    .min(1, 'Plate number is required')
    .regex(plateNumberRegex, 'Invalid plate number format'),

  type: vehicleTypeSchema,

  make: z
    .string()
    .min(1, 'Make is required')
    .max(50, 'Make must be less than 50 characters'),

  model: z
    .string()
    .min(1, 'Model is required')
    .max(50, 'Model must be less than 50 characters'),

  year: z
    .number()
    .int('Year must be a whole number')
    .min(1990, 'Year must be 1990 or later')
    .max(new Date().getFullYear() + 1, 'Invalid year'),

  color: z
    .string()
    .max(30, 'Color must be less than 30 characters')
    .optional(),

  fuel_type: fuelTypeSchema,

  ownership: ownershipSchema,

  status: vehicleStatusSchema.optional().default('available'),

  mileage: z
    .number()
    .int('Mileage must be a whole number')
    .nonnegative('Mileage cannot be negative')
    .optional(),

  vin: z
    .string()
    .regex(vinRegex, 'Invalid VIN format (must be 17 characters)')
    .optional()
    .or(z.literal('')),

  purchase_date: z
    .string()
    .optional()
    .refine(
      (val) => !val || !isNaN(Date.parse(val)),
      'Invalid date format'
    ),

  registration_expiry: z
    .string()
    .optional()
    .refine(
      (val) => !val || !isNaN(Date.parse(val)),
      'Invalid date format'
    ),

  insurance_expiry: z
    .string()
    .optional()
    .refine(
      (val) => !val || !isNaN(Date.parse(val)),
      'Invalid date format'
    ),

  gps_device_id: z
    .string()
    .max(50, 'GPS Device ID must be less than 50 characters')
    .optional(),

  assigned_to_city: z
    .string()
    .max(100, 'City must be less than 100 characters')
    .optional(),
})

/**
 * Type inference for VehicleFormData
 */
export type VehicleFormData = z.infer<typeof vehicleSchema>

/**
 * Vehicle filter schema
 */
export const vehicleFilterSchema = z.object({
  type: vehicleTypeSchema.optional(),
  status: vehicleStatusSchema.optional(),
  fuel_type: fuelTypeSchema.optional(),
  city: z.string().optional(),
  search: z.string().optional(),
  page: z.number().int().positive().optional().default(1),
  limit: z.number().int().positive().max(100).optional().default(20),
})

export type VehicleFilterData = z.infer<typeof vehicleFilterSchema>

/**
 * Vehicle assignment schema
 */
export const vehicleAssignmentSchema = z.object({
  vehicle_id: z.number().int().positive('Vehicle ID is required'),
  courier_id: z.number().int().positive('Courier ID is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  notes: z.string().max(500).optional(),
})

export type VehicleAssignmentData = z.infer<typeof vehicleAssignmentSchema>

/**
 * Maintenance record schema
 */
export const maintenanceSchema = z.object({
  vehicle_id: z.number().int().positive('Vehicle ID is required'),
  maintenance_type: z.enum([
    'oil_change',
    'tire_rotation',
    'brake_service',
    'engine_repair',
    'scheduled_service',
    'accident_repair',
    'other',
  ]),
  description: z.string().min(1, 'Description is required').max(1000),
  cost: z.number().nonnegative('Cost cannot be negative'),
  mileage_at_service: z.number().int().nonnegative().optional(),
  service_date: z.string().min(1, 'Service date is required'),
  next_service_date: z.string().optional(),
  vendor: z.string().max(100).optional(),
  invoice_number: z.string().max(50).optional(),
})

export type MaintenanceFormData = z.infer<typeof maintenanceSchema>
