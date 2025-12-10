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
export const workflowTemplateFormSchema = z.object({
  name: z.string().min(1, 'Workflow name is required'),
  template_code: z.string().min(1, 'Template code is required'),
  description: z
    .string()
    .min(1, 'Description is required')
    .min(20, 'Description must be at least 20 characters'),
  category: workflowCategorySchema,
  steps: z.string().min(1, 'Workflow steps are required'),
  approval_chain: z.string().min(1, 'Approval chain is required'),
  estimated_duration: z.number().int().positive('Estimated duration must be greater than zero'),
  auto_assign: z.boolean(),
  status: workflowStatusSchema,
  trigger_type: workflowTriggerTypeSchema,
  conditions: z.string(),
  notifications: z.string(),
  notes: z.string(),
})

export type WorkflowTemplateFormData = z.infer<typeof workflowTemplateFormSchema>

/**
 * Workflow instance status enum schema
 */
export const workflowInstanceStatusSchema = z.enum([
  'pending',
  'in_progress',
  'awaiting_approval',
  'approved',
  'rejected',
  'completed',
  'cancelled',
])

/**
 * Workflow instance schema
 */
export const workflowInstanceSchema = z.object({
  template_id: z.string().min(1, 'Template is required'),
  reference_id: z.string().min(1, 'Reference ID is required'),
  reference_type: z.string().min(1, 'Reference type is required'),
  current_step: z.number().int().nonnegative(),
  status: workflowInstanceStatusSchema,
  started_by: z.string().min(1, 'Initiator is required'),
  assigned_to: z.string().optional(),
  notes: z.string(),
})

export type WorkflowInstanceFormData = z.infer<typeof workflowInstanceSchema>
