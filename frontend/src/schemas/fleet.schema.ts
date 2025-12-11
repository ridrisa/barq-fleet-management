import { z } from 'zod'

/**
 * Phone number validation
 */
const phoneRegex = /^\+?[\d\s\-()]{8,20}$/

// ============================================
// ASSIGNMENT SCHEMA
// ============================================

/**
 * Assignment type enum
 */
export const assignmentTypeSchema = z.enum(['permanent', 'temporary', 'shift_based'])

/**
 * Assignment status enum
 */
export const assignmentStatusSchema = z.enum(['active', 'completed', 'cancelled'])

/**
 * Shift type enum
 */
export const shiftTypeSchema = z.enum(['morning', 'evening', 'night'])

/**
 * Assignment form validation schema
 */
export const assignmentSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  vehicle_id: z.string().min(1, 'Vehicle is required'),
  assignment_type: assignmentTypeSchema,
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  shift: shiftTypeSchema.optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
  status: assignmentStatusSchema,
}).refine(
  (data) => {
    if (data.end_date && data.start_date) {
      return new Date(data.end_date) >= new Date(data.start_date)
    }
    return true
  },
  {
    message: 'End date must be after start date',
    path: ['end_date'],
  }
).refine(
  (data) => {
    if (data.assignment_type === 'shift_based' && !data.shift) {
      return false
    }
    return true
  },
  {
    message: 'Shift is required for shift-based assignments',
    path: ['shift'],
  }
)

export type AssignmentFormData = z.infer<typeof assignmentSchema>

// ============================================
// FUEL LOG SCHEMA
// ============================================

/**
 * Fuel type enum
 */
export const fuelTypeSchema = z.enum(['petrol', 'diesel', 'electric'])

/**
 * Fuel log form validation schema
 */
export const fuelLogSchema = z.object({
  vehicle_id: z.string().min(1, 'Vehicle is required'),
  date: z.string().min(1, 'Date is required'),
  fuel_type: fuelTypeSchema,
  liters: z.number().positive('Liters must be greater than 0'),
  cost: z.number().positive('Cost must be greater than 0'),
  odometer: z.number().positive('Odometer reading must be greater than 0'),
  station: z.string().max(100, 'Station name must be less than 100 characters').optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
})

export type FuelLogFormData = z.infer<typeof fuelLogSchema>

// ============================================
// ROUTE SCHEMA
// ============================================

/**
 * Route status enum
 */
export const routeStatusSchema = z.enum(['active', 'inactive', 'under_review'])

/**
 * Route type enum
 */
export const routeTypeSchema = z.enum(['delivery', 'pickup', 'mixed'])

/**
 * Route form validation schema
 */
export const routeSchema = z.object({
  name: z.string().min(1, 'Route name is required').max(100, 'Route name must be less than 100 characters'),
  route_code: z.string().min(1, 'Route code is required').max(20, 'Route code must be less than 20 characters'),
  start_point: z.string().min(1, 'Start point is required').max(200, 'Start point must be less than 200 characters'),
  end_point: z.string().min(1, 'End point is required').max(200, 'End point must be less than 200 characters'),
  waypoints: z.string().max(500, 'Waypoints must be less than 500 characters').optional(),
  distance: z.number().positive('Distance must be greater than zero'),
  estimated_duration: z.number().positive('Estimated duration must be greater than zero'),
  status: routeStatusSchema,
  route_type: routeTypeSchema,
  assigned_courier: z.string().optional(),
  service_days: z.string().max(50, 'Service days must be less than 50 characters').optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
})

export type RouteFormData = z.infer<typeof routeSchema>

// ============================================
// COD (Cash on Delivery) SCHEMA
// ============================================

/**
 * Currency enum
 */
export const currencySchema = z.enum(['SAR', 'USD', 'EUR'])

/**
 * Payment method enum
 */
export const paymentMethodSchema = z.enum(['cash', 'card', 'online'])

/**
 * COD status enum
 */
export const codStatusSchema = z.enum(['pending', 'collected', 'reconciled', 'disputed'])

/**
 * COD form validation schema
 */
export const codSchema = z.object({
  delivery_id: z.string().min(1, 'Delivery ID is required'),
  courier_id: z.string().min(1, 'Courier is required'),
  amount: z.number().positive('Amount must be greater than zero'),
  currency: currencySchema,
  collected: z.boolean(),
  collection_date: z.string().optional(),
  reconciled: z.boolean(),
  reconciliation_date: z.string().optional(),
  payment_method: paymentMethodSchema,
  reference_number: z.string().max(50, 'Reference number must be less than 50 characters').optional(),
  status: codStatusSchema,
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
}).refine(
  (data) => {
    if (data.collected && !data.collection_date) {
      return false
    }
    return true
  },
  {
    message: 'Collection date is required when marked as collected',
    path: ['collection_date'],
  }
).refine(
  (data) => {
    if (data.reconciled && !data.reconciliation_date) {
      return false
    }
    return true
  },
  {
    message: 'Reconciliation date is required when marked as reconciled',
    path: ['reconciliation_date'],
  }
)

export type CODFormData = z.infer<typeof codSchema>

// ============================================
// ZONE SCHEMA
// ============================================

/**
 * Zone status enum
 */
export const zoneStatusSchema = z.enum(['active', 'inactive', 'full'])

/**
 * Zone form validation schema
 */
export const zoneSchema = z.object({
  zone_name: z.string().min(1, 'Zone name is required').max(100, 'Zone name must be less than 100 characters'),
  zone_code: z.string().min(1, 'Zone code is required').max(20, 'Zone code must be less than 20 characters'),
  areas: z.string().max(500, 'Areas must be less than 500 characters').optional(),
  coverage_radius: z.number().nonnegative('Coverage radius cannot be negative').optional(),
  assigned_couriers: z.number().int().nonnegative('Assigned couriers cannot be negative'),
  max_capacity: z.number().int().positive('Max capacity must be greater than 0'),
  status: zoneStatusSchema,
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
})

export type ZoneFormData = z.infer<typeof zoneSchema>

// ============================================
// PRIORITY QUEUE SCHEMA
// ============================================

/**
 * Priority level enum
 */
export const priorityLevelSchema = z.enum(['express', 'same_day', 'standard', 'deferred'])

/**
 * Priority queue form validation schema (for adding/updating delivery priority)
 */
export const priorityQueueSchema = z.object({
  delivery_id: z.string().min(1, 'Delivery ID is required'),
  priority: priorityLevelSchema,
  sla_deadline: z.string().optional(),
  courier_id: z.string().optional(),
  reason: z.string().max(200, 'Reason must be less than 200 characters').optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
})

export type PriorityQueueFormData = z.infer<typeof priorityQueueSchema>

// ============================================
// TRACKING UPDATE SCHEMA
// ============================================

/**
 * Tracking status enum
 */
export const trackingStatusSchema = z.enum([
  'pending',
  'assigned',
  'picked_up',
  'in_transit',
  'out_for_delivery',
  'delivered',
  'failed',
  'returned',
  'cancelled',
])

/**
 * Tracking update form validation schema
 */
export const trackingUpdateSchema = z.object({
  delivery_id: z.string().min(1, 'Delivery ID is required'),
  status: trackingStatusSchema,
  location: z.string().max(200, 'Location must be less than 200 characters').optional(),
  latitude: z.number().min(-90).max(90).optional(),
  longitude: z.number().min(-180).max(180).optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
  photo_url: z.string().url('Invalid photo URL').optional().or(z.literal('')),
  signature_url: z.string().url('Invalid signature URL').optional().or(z.literal('')),
  failure_reason: z.string().max(200, 'Failure reason must be less than 200 characters').optional(),
  recipient_name: z.string().max(100, 'Recipient name must be less than 100 characters').optional(),
})

export type TrackingUpdateFormData = z.infer<typeof trackingUpdateSchema>

// ============================================
// DELIVERY FORM SCHEMA (simplified for the form)
// ============================================

/**
 * Delivery status enum
 */
export const deliveryStatusSchema = z.enum([
  'pending',
  'assigned',
  'in_transit',
  'delivered',
  'failed',
  'cancelled',
])

/**
 * Delivery priority enum
 */
export const deliveryPrioritySchema = z.enum(['low', 'normal', 'high', 'urgent'])

/**
 * Delivery form validation schema
 */
export const deliveryFormSchema = z.object({
  courier_id: z.string().optional(),
  tracking_number: z.string().min(1, 'Tracking number is required').max(50, 'Tracking number must be less than 50 characters'),
  status: deliveryStatusSchema,
  priority: deliveryPrioritySchema,
  pickup_address: z.string().min(1, 'Pickup address is required').max(300, 'Pickup address must be less than 300 characters'),
  delivery_address: z.string().min(1, 'Delivery address is required').max(300, 'Delivery address must be less than 300 characters'),
  recipient_name: z.string().min(1, 'Recipient name is required').max(100, 'Recipient name must be less than 100 characters'),
  recipient_phone: z.string().min(1, 'Recipient phone is required').regex(phoneRegex, 'Invalid phone number format'),
  package_type: z.string().max(50, 'Package type must be less than 50 characters').optional(),
  weight: z.number().nonnegative('Weight cannot be negative').optional(),
  dimensions: z.string().max(50, 'Dimensions must be less than 50 characters').optional(),
  scheduled_date: z.string().optional(),
  delivered_date: z.string().optional(),
  delivery_proof: z.string().max(200, 'Delivery proof must be less than 200 characters').optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
})

export type DeliveryFormData = z.infer<typeof deliveryFormSchema>

// ============================================
// HANDOVER SCHEMA (move from formConfigs)
// ============================================

/**
 * Checklist item schema
 */
export const checklistItemSchema = z.object({
  id: z.string(),
  label: z.string(),
  checked: z.boolean(),
})

/**
 * Handover form validation schema
 */
export const handoverSchema = z.object({
  from_courier: z.string().min(1, 'From courier is required'),
  to_courier: z.string().min(1, 'To courier is required'),
  vehicle_id: z.string().optional(),
  handover_date: z.string().min(1, 'Handover date is required'),
  checklist: z.array(checklistItemSchema).optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
  signature: z.string().optional(),
}).refine(
  (data) => data.from_courier !== data.to_courier || !data.from_courier,
  {
    message: 'Cannot hand over to the same courier',
    path: ['to_courier'],
  }
)

export type HandoverFormData = z.infer<typeof handoverSchema>

/**
 * Default handover checklist items
 */
export const defaultHandoverChecklist = [
  { id: '1', label: 'Vehicle keys handed over', checked: false },
  { id: '2', label: 'Vehicle condition verified', checked: false },
  { id: '3', label: 'Fuel level noted', checked: false },
  { id: '4', label: 'Documents transferred', checked: false },
  { id: '5', label: 'Pending deliveries briefed', checked: false },
  { id: '6', label: 'Equipment checked', checked: false },
  { id: '7', label: 'Cash/COD reconciled', checked: false },
]

// ============================================
// MAINTENANCE FORM SCHEMA (for scheduling)
// ============================================

/**
 * Maintenance status enum
 */
export const maintenanceStatusSchema = z.enum(['scheduled', 'in_progress', 'completed', 'cancelled'])

/**
 * Maintenance type enum
 */
export const maintenanceTypeSchema = z.enum([
  'oil_change',
  'tire_replacement',
  'brake_service',
  'battery_replacement',
  'inspection',
  'general_repair',
  'ac_service',
  'transmission',
  'other',
])

/**
 * Maintenance form validation schema
 */
export const maintenanceFormSchema = z.object({
  vehicle_id: z.string().min(1, 'Vehicle is required'),
  maintenance_type: maintenanceTypeSchema,
  scheduled_date: z.string().min(1, 'Scheduled date is required'),
  completed_date: z.string().optional(),
  status: maintenanceStatusSchema,
  cost: z.number().nonnegative('Cost cannot be negative').optional(),
  service_provider: z.string().max(100, 'Service provider must be less than 100 characters').optional(),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
}).refine(
  (data) => {
    if (data.status === 'completed' && !data.completed_date) {
      return false
    }
    return true
  },
  {
    message: 'Completed date is required when status is completed',
    path: ['completed_date'],
  }
)

export type MaintenanceFormData = z.infer<typeof maintenanceFormSchema>
