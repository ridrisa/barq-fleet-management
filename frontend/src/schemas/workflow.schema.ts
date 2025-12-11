import { z } from 'zod'

/**
 * Workflow category enum schema
 */
export const workflowCategorySchema = z.enum([
  'courier',
  'vehicle',
  'delivery',
  'hr',
  'finance',
  'general',
])

/**
 * Workflow status enum schema
 */
export const workflowStatusSchema = z.enum(['active', 'draft', 'archived'])

/**
 * Workflow trigger type enum schema
 */
export const workflowTriggerTypeSchema = z.enum(['manual', 'automatic', 'scheduled'])

/**
 * Workflow template form validation schema
 */
export const workflowTemplateSchema = z.object({
  name: z
    .string()
    .min(1, 'Workflow name is required')
    .max(200, 'Workflow name must be less than 200 characters'),

  template_code: z
    .string()
    .min(1, 'Template code is required')
    .max(50, 'Template code must be less than 50 characters'),

  description: z
    .string()
    .min(1, 'Description is required')
    .min(20, 'Description must be at least 20 characters')
    .max(1000, 'Description must be less than 1000 characters'),

  category: workflowCategorySchema,

  steps: z
    .string()
    .min(1, 'Workflow steps are required')
    .max(2000, 'Steps must be less than 2000 characters'),

  approval_chain: z
    .string()
    .min(1, 'Approval chain is required')
    .max(500, 'Approval chain must be less than 500 characters'),

  estimated_duration: z
    .number()
    .positive('Estimated duration must be greater than zero')
    .max(8760, 'Estimated duration cannot exceed 1 year (8760 hours)'),

  auto_assign: z.boolean(),

  status: workflowStatusSchema,

  trigger_type: workflowTriggerTypeSchema,

  conditions: z
    .string()
    .max(1000, 'Conditions must be less than 1000 characters')
    .optional()
    .or(z.literal('')),

  notifications: z
    .string()
    .max(500, 'Notifications must be less than 500 characters')
    .optional()
    .or(z.literal('')),

  notes: z
    .string()
    .max(2000, 'Notes must be less than 2000 characters')
    .optional()
    .or(z.literal('')),
})

export type WorkflowTemplateFormData = z.infer<typeof workflowTemplateSchema>
export type WorkflowCategory = z.infer<typeof workflowCategorySchema>
export type WorkflowStatus = z.infer<typeof workflowStatusSchema>
export type WorkflowTriggerType = z.infer<typeof workflowTriggerTypeSchema>
