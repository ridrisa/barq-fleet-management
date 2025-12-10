import { z } from 'zod'

/**
 * Courier Status enum
 */
export const courierStatusSchema = z.enum(['active', 'on_leave', 'terminated', 'suspended'])

/**
 * Phone number validation regex
 * Supports international formats: +971 50 123 4567, +966501234567, etc.
 */
const phoneRegex = /^\+?[\d\s\-()]{8,20}$/

/**
 * Saudi/UAE national ID validation (10-digit format)
 */
const nationalIdRegex = /^\d{10}$/

/**
 * Courier form validation schema
 */
export const courierSchema = z.object({
  employee_id: z
    .string()
    .min(1, 'Employee ID is required')
    .max(50, 'Employee ID must be less than 50 characters'),

  name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),

  phone: z
    .string()
    .min(1, 'Phone number is required')
    .regex(phoneRegex, 'Invalid phone number format'),

  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),

  status: courierStatusSchema.optional().default('active'),

  joining_date: z
    .string()
    .optional()
    .refine(
      (val) => !val || !isNaN(Date.parse(val)),
      'Invalid date format'
    ),

  license_number: z
    .string()
    .max(50, 'License number must be less than 50 characters')
    .optional(),

  license_expiry: z
    .string()
    .optional()
    .refine(
      (val) => !val || new Date(val) > new Date(),
      'License has expired'
    ),

  national_id: z
    .string()
    .regex(nationalIdRegex, 'National ID must be 10 digits')
    .optional()
    .or(z.literal('')),

  emergency_contact: z
    .string()
    .regex(phoneRegex, 'Invalid emergency contact format')
    .optional()
    .or(z.literal('')),

  address: z
    .string()
    .max(500, 'Address must be less than 500 characters')
    .optional(),

  city: z
    .string()
    .max(100, 'City must be less than 100 characters')
    .optional(),

  bank_name: z
    .string()
    .max(100, 'Bank name must be less than 100 characters')
    .optional(),

  bank_account_number: z
    .string()
    .max(30, 'Account number must be less than 30 characters')
    .optional(),

  iban: z
    .string()
    .max(34, 'IBAN must be less than 34 characters')
    .optional(),
})

/**
 * Type inference for CourierFormData
 */
export type CourierFormData = z.infer<typeof courierSchema>

/**
 * Courier search/filter schema
 */
export const courierFilterSchema = z.object({
  status: courierStatusSchema.optional(),
  city: z.string().optional(),
  search: z.string().optional(),
  page: z.number().int().positive().optional().default(1),
  limit: z.number().int().positive().max(100).optional().default(20),
})

export type CourierFilterData = z.infer<typeof courierFilterSchema>

/**
 * Courier document upload schema
 */
export const courierDocumentSchema = z.object({
  document_type: z.enum([
    'national_id',
    'driving_license',
    'passport',
    'employment_contract',
    'medical_certificate',
    'other',
  ]),
  file: z.instanceof(File).refine(
    (file) => file.size <= 10 * 1024 * 1024, // 10MB max
    'File size must be less than 10MB'
  ),
  expiry_date: z.string().optional(),
  notes: z.string().max(500).optional(),
})

export type CourierDocumentData = z.infer<typeof courierDocumentSchema>
