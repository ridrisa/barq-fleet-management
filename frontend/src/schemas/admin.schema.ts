import { z } from 'zod'

/**
 * User role enum schema
 */
export const userRoleAdminSchema = z.enum(['admin', 'manager', 'user', 'viewer'])

/**
 * User form validation schema
 */
export const userFormSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  full_name: z
    .string()
    .min(1, 'Full name is required')
    .min(2, 'Full name must be at least 2 characters'),
  password: z.string().optional(),
  role: userRoleAdminSchema,
  is_active: z.boolean(),
  department: z.string(),
  phone: z
    .string()
    .regex(/^[+]?[\d\s\-()]{10,}$/, 'Please enter a valid phone number')
    .or(z.literal('')),
})

/**
 * User form schema for create mode (password required)
 */
export const userCreateSchema = userFormSchema.extend({
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
})

/**
 * User form schema for edit mode (password optional)
 */
export const userEditSchema = userFormSchema.extend({
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters if provided')
    .optional()
    .or(z.literal('')),
})

export type UserFormData = z.infer<typeof userFormSchema>
export type UserCreateFormData = z.infer<typeof userCreateSchema>
export type UserEditFormData = z.infer<typeof userEditSchema>

/**
 * Asset type enum schema
 */
export const assetTypeSchema = z.enum(['vehicle', 'equipment', 'device', 'furniture', 'other'])

/**
 * Asset condition enum schema
 */
export const assetConditionSchema = z.enum(['new', 'good', 'fair', 'poor'])

/**
 * Asset status enum schema
 */
export const assetStatusSchema = z.enum(['available', 'assigned', 'maintenance', 'disposed'])

/**
 * Asset form validation schema
 */
export const assetFormSchema = z.object({
  asset_name: z.string().min(1, 'Asset name is required'),
  asset_type: assetTypeSchema,
  asset_code: z.string().min(1, 'Asset code is required'),
  purchase_date: z.string().min(1, 'Purchase date is required'),
  value: z.number().positive('Asset value must be greater than zero'),
  assigned_to: z.string(),
  condition: assetConditionSchema,
  status: assetStatusSchema,
  warranty_expiry: z.string(),
  supplier: z.string(),
  serial_number: z.string(),
  notes: z.string(),
})

export type AssetFormData = z.infer<typeof assetFormSchema>

/**
 * Allocation status enum schema
 */
export const allocationStatusSchema = z.enum(['active', 'pending', 'ended'])

/**
 * Allocation form validation schema
 */
export const allocationFormSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  building_id: z.string().min(1, 'Building is required'),
  room_id: z.string().min(1, 'Room is required'),
  bed_id: z.string().min(1, 'Bed is required'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  status: allocationStatusSchema,
  notes: z.string(),
}).refine(
  (data) => {
    if (data.end_date && data.start_date) {
      return new Date(data.end_date) >= new Date(data.start_date)
    }
    return true
  },
  {
    message: 'End date cannot be before start date',
    path: ['end_date'],
  }
).refine(
  (data) => {
    if (data.status === 'ended' && !data.end_date) {
      return false
    }
    return true
  },
  {
    message: 'End date is required when status is ended',
    path: ['end_date'],
  }
)

export type AllocationFormData = z.infer<typeof allocationFormSchema>

/**
 * Building status enum schema
 */
export const buildingStatusSchema = z.enum(['active', 'under_construction', 'maintenance', 'closed'])

/**
 * Building form validation schema
 */
export const buildingFormSchema = z.object({
  name: z.string().min(1, 'Building name is required'),
  building_code: z.string().min(1, 'Building code is required'),
  address: z.string().min(1, 'Address is required'),
  city: z.string().min(1, 'City is required'),
  country: z.string(),
  capacity: z.number().int().positive('Capacity must be greater than zero'),
  floors: z.number().int().positive('Number of floors must be at least 1'),
  total_rooms: z.number().int().nonnegative(),
  amenities: z.string(),
  manager: z.string().min(1, 'Manager name is required'),
  manager_contact: z
    .string()
    .min(1, 'Manager contact is required')
    .regex(/^\+?[\d\s\-()]+$/, 'Invalid phone number format'),
  status: buildingStatusSchema,
  construction_year: z.number().int().min(1900).max(2100).optional(),
  monthly_rent: z.number().nonnegative(),
  notes: z.string(),
})

export type BuildingFormData = z.infer<typeof buildingFormSchema>
