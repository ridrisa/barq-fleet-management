import { z } from 'zod'

/**
 * User role enum schema
 */
export const userFormRoleSchema = z.enum(['admin', 'manager', 'user', 'viewer'])

/**
 * Base user form validation schema
 */
const baseUserSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),

  full_name: z
    .string()
    .min(1, 'Full name is required')
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must be less than 100 characters'),

  role: userFormRoleSchema,

  is_active: z.boolean(),

  department: z
    .string()
    .max(100, 'Department must be less than 100 characters')
    .optional()
    .or(z.literal('')),

  phone: z
    .string()
    .regex(/^[+]?[\d\s\-()]{10,}$/, 'Please enter a valid phone number')
    .optional()
    .or(z.literal('')),
})

/**
 * User form schema for create mode (password required)
 */
export const userCreateSchema = baseUserSchema.extend({
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters'),
})

/**
 * User form schema for edit mode (password optional)
 */
export const userEditSchema = baseUserSchema.extend({
  password: z
    .string()
    .optional()
    .refine(
      (val) => !val || val.length >= 8,
      'Password must be at least 8 characters if provided'
    ),
})

/**
 * Combined schema for general use
 */
export const userSchema = baseUserSchema.extend({
  password: z.string().optional(),
})

export type UserFormData = z.infer<typeof userSchema>
export type UserCreateFormData = z.infer<typeof userCreateSchema>
export type UserEditFormData = z.infer<typeof userEditSchema>
