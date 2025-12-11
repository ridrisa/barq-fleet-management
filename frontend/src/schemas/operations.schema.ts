import { z } from 'zod'

/**
 * Incident type enum schema
 */
export const incidentTypeSchema = z.enum([
  'accident',
  'theft',
  'damage',
  'complaint',
  'injury',
  'other',
])

/**
 * Incident severity enum schema
 */
export const incidentSeveritySchema = z.enum(['low', 'medium', 'high', 'critical'])

/**
 * Incident status enum schema
 */
export const incidentStatusSchema = z.enum(['open', 'investigating', 'resolved', 'closed'])

/**
 * Incident report form validation schema
 */
export const incidentReportSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),

  incident_type: z
    .string()
    .min(1, 'Incident type is required'),

  severity: incidentSeveritySchema,

  location: z
    .string()
    .max(500, 'Location must be less than 500 characters')
    .optional()
    .or(z.literal('')),

  description: z
    .string()
    .min(1, 'Description is required')
    .min(10, 'Description must be at least 10 characters')
    .max(5000, 'Description must be less than 5000 characters'),

  status: incidentStatusSchema,

  reported_by: z
    .string()
    .max(200, 'Reporter name must be less than 200 characters')
    .optional()
    .or(z.literal('')),

  evidence_urls: z
    .array(z.string().url('Invalid URL'))
    .optional(),
})

/**
 * Quality control status enum schema
 */
export const qualityControlStatusSchema = z.enum(['pending', 'in_progress', 'completed'])

/**
 * Quality control form validation schema
 */
export const qualityControlSchema = z.object({
  delivery_id: z
    .string()
    .min(1, 'Delivery ID is required')
    .max(100, 'Delivery ID must be less than 100 characters'),

  inspector: z
    .string()
    .min(1, 'Inspector is required'),

  check_date: z
    .string()
    .min(1, 'Date is required')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Invalid date format (YYYY-MM-DD)'),

  passed: z.boolean(),

  issues: z
    .string()
    .max(2000, 'Issues description must be less than 2000 characters')
    .optional()
    .or(z.literal('')),

  corrective_action: z
    .string()
    .max(2000, 'Corrective action must be less than 2000 characters')
    .optional()
    .or(z.literal('')),

  status: qualityControlStatusSchema,
})

export type IncidentReportFormData = z.infer<typeof incidentReportSchema>
export type IncidentType = z.infer<typeof incidentTypeSchema>
export type IncidentSeverity = z.infer<typeof incidentSeveritySchema>
export type IncidentStatus = z.infer<typeof incidentStatusSchema>

export type QualityControlFormData = z.infer<typeof qualityControlSchema>
export type QualityControlStatus = z.infer<typeof qualityControlStatusSchema>
