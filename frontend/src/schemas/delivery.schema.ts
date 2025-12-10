import { z } from 'zod'

/**
 * Delivery status enum schema
 */
export const deliveryStatusSchema = z.enum([
  'pending',
  'assigned',
  'picked_up',
  'in_transit',
  'delivered',
  'failed',
  'cancelled',
  'returned',
])

/**
 * Delivery priority enum schema
 */
export const deliveryPrioritySchema = z.enum([
  'low',
  'normal',
  'high',
  'urgent',
])

/**
 * Phone number validation
 */
const phoneRegex = /^\+?[\d\s\-()]{8,20}$/

/**
 * Coordinate validation
 */
const latitudeSchema = z.number().min(-90).max(90)
const longitudeSchema = z.number().min(-180).max(180)

/**
 * Address schema for pickup/delivery locations
 */
export const addressSchema = z.object({
  street: z.string().min(1, 'Street address is required').max(200),
  city: z.string().min(1, 'City is required').max(100),
  district: z.string().max(100).optional(),
  building: z.string().max(50).optional(),
  floor: z.string().max(20).optional(),
  apartment: z.string().max(20).optional(),
  postal_code: z.string().max(20).optional(),
  country: z.string().max(50).optional().default('Saudi Arabia'),
  latitude: latitudeSchema.optional(),
  longitude: longitudeSchema.optional(),
  notes: z.string().max(500).optional(),
})

export type AddressFormData = z.infer<typeof addressSchema>

/**
 * Contact schema for sender/recipient
 */
export const contactSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  phone: z.string().min(1, 'Phone is required').regex(phoneRegex, 'Invalid phone format'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  company: z.string().max(100).optional(),
})

export type ContactFormData = z.infer<typeof contactSchema>

/**
 * Package details schema
 */
export const packageSchema = z.object({
  weight: z.number().positive('Weight must be positive').max(1000, 'Weight exceeds maximum'),
  length: z.number().positive().max(500).optional(),
  width: z.number().positive().max(500).optional(),
  height: z.number().positive().max(500).optional(),
  quantity: z.number().int().positive().max(100).optional().default(1),
  description: z.string().max(500).optional(),
  fragile: z.boolean().optional().default(false),
  requires_signature: z.boolean().optional().default(false),
  cod_amount: z.number().nonnegative().optional(),
})

export type PackageFormData = z.infer<typeof packageSchema>

/**
 * Delivery creation form validation schema
 */
export const deliverySchema = z.object({
  // Reference
  tracking_number: z.string().max(50).optional(),
  external_reference: z.string().max(100).optional(),

  // Sender
  sender: contactSchema,
  pickup_address: addressSchema,

  // Recipient
  recipient: contactSchema,
  delivery_address: addressSchema,

  // Package
  package: packageSchema,

  // Scheduling
  pickup_date: z.string().min(1, 'Pickup date is required'),
  pickup_time_from: z.string().optional(),
  pickup_time_to: z.string().optional(),
  delivery_date: z.string().optional(),
  delivery_time_from: z.string().optional(),
  delivery_time_to: z.string().optional(),

  // Options
  priority: deliveryPrioritySchema.optional().default('normal'),
  service_type: z.enum(['standard', 'express', 'same_day', 'scheduled']).optional().default('standard'),
  notes: z.string().max(1000).optional(),

  // Assignment
  courier_id: z.number().int().positive().optional(),
  vehicle_id: z.number().int().positive().optional(),
})

export type DeliveryFormData = z.infer<typeof deliverySchema>

/**
 * Delivery filter schema
 */
export const deliveryFilterSchema = z.object({
  status: deliveryStatusSchema.optional(),
  priority: deliveryPrioritySchema.optional(),
  courier_id: z.number().int().positive().optional(),
  date_from: z.string().optional(),
  date_to: z.string().optional(),
  city: z.string().optional(),
  search: z.string().optional(),
  page: z.number().int().positive().optional().default(1),
  limit: z.number().int().positive().max(100).optional().default(20),
})

export type DeliveryFilterData = z.infer<typeof deliveryFilterSchema>

/**
 * Delivery status update schema
 */
export const deliveryStatusUpdateSchema = z.object({
  status: deliveryStatusSchema,
  notes: z.string().max(500).optional(),
  location: z.object({
    latitude: latitudeSchema,
    longitude: longitudeSchema,
  }).optional(),
  signature_url: z.string().url().optional(),
  photo_url: z.string().url().optional(),
  failure_reason: z.string().max(500).optional(),
})

export type DeliveryStatusUpdateData = z.infer<typeof deliveryStatusUpdateSchema>

/**
 * Bulk delivery assignment schema
 */
export const bulkAssignmentSchema = z.object({
  delivery_ids: z.array(z.number().int().positive()).min(1, 'Select at least one delivery'),
  courier_id: z.number().int().positive('Courier is required'),
  notes: z.string().max(500).optional(),
})

export type BulkAssignmentData = z.infer<typeof bulkAssignmentSchema>
