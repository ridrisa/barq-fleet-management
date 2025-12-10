import { z } from 'zod'

/**
 * User role enum schema
 */
export const userRoleSchema = z.enum([
  'super_admin',
  'admin',
  'hr_manager',
  'fleet_manager',
  'viewer',
  'user',
])

/**
 * Password validation rules:
 * - At least 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one number
 * - At least one special character
 */
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/

/**
 * Login form validation schema
 */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),

  password: z
    .string()
    .min(1, 'Password is required'),
})

export type LoginFormData = z.infer<typeof loginSchema>

/**
 * Registration form validation schema
 */
export const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),

  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      passwordRegex,
      'Password must contain uppercase, lowercase, number, and special character'
    ),

  confirm_password: z.string().min(1, 'Please confirm your password'),

  full_name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),

  role: userRoleSchema.optional().default('user'),
}).refine((data) => data.password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

export type RegisterFormData = z.infer<typeof registerSchema>

/**
 * Forgot password form validation schema
 */
export const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
})

export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>

/**
 * Reset password form validation schema
 */
export const resetPasswordSchema = z.object({
  token: z.string().min(1, 'Reset token is required'),

  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      passwordRegex,
      'Password must contain uppercase, lowercase, number, and special character'
    ),

  confirm_password: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>

/**
 * Change password form validation schema
 */
export const changePasswordSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),

  new_password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      passwordRegex,
      'Password must contain uppercase, lowercase, number, and special character'
    ),

  confirm_password: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
}).refine((data) => data.current_password !== data.new_password, {
  message: 'New password must be different from current password',
  path: ['new_password'],
})

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

/**
 * User profile update schema
 */
export const userProfileSchema = z.object({
  full_name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters')
    .optional(),

  phone: z
    .string()
    .regex(/^\+?[\d\s\-()]{8,20}$/, 'Invalid phone number')
    .optional()
    .or(z.literal('')),

  avatar_url: z
    .string()
    .url('Invalid URL')
    .optional()
    .or(z.literal('')),

  timezone: z
    .string()
    .max(50)
    .optional(),

  language: z
    .enum(['en', 'ar'])
    .optional()
    .default('en'),
})

export type UserProfileFormData = z.infer<typeof userProfileSchema>
