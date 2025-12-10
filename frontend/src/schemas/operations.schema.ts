import { z } from 'zod'

// ============================================
// SERVICE LEVEL (SLA) SCHEMAS
// ============================================

/**
 * SLA time unit enum schema
 */
export const slaTimeUnitSchema = z.enum(['minutes', 'hours', 'days'])

/**
 * SLA measurement period enum schema
 */
export const slaMeasurementPeriodSchema = z.enum(['daily', 'weekly', 'monthly'])

/**
 * Service Level Agreement form validation schema
 * Note: Uses defaults because it's used with DynamicForm
 */
export const serviceLevelFormSchema = z.object({
  service_type: z.string().min(1, 'Service type is required'),
  target_time: z.number().positive('Target time must be greater than 0'),
  time_unit: slaTimeUnitSchema.default('hours'),
  measurement: z.string().default(''),
  penalty_amount: z.number().nonnegative().default(0),
  measurement_period: slaMeasurementPeriodSchema.default('monthly'),
  is_active: z.boolean().default(true),
})

export type ServiceLevelFormData = z.infer<typeof serviceLevelFormSchema>

// ============================================
// INCIDENT REPORTING SCHEMAS
// ============================================

/**
 * Incident severity enum schema
 */
export const incidentSeveritySchema = z.enum(['low', 'medium', 'high', 'critical'])

/**
 * Incident status enum schema
 */
export const incidentStatusSchema = z.enum(['open', 'investigating', 'resolved', 'closed'])

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
 * Incident report form validation schema
 */
export const incidentFormSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  incident_type: z.string().min(1, 'Incident type is required'),
  severity: incidentSeveritySchema,
  location: z.string(),
  description: z.string().min(1, 'Description is required'),
  status: incidentStatusSchema,
  reported_by: z.string(),
  evidence_urls: z.array(z.string()),
})

export type IncidentReportFormData = z.infer<typeof incidentFormSchema>

// ============================================
// QUALITY CONTROL SCHEMAS
// ============================================

/**
 * Quality control status enum schema
 */
export const qualityControlStatusSchema = z.enum(['pending', 'in_progress', 'completed'])

/**
 * Quality control checklist item schema
 */
export const checklistItemSchema = z.object({
  id: z.string(),
  label: z.string(),
  checked: z.boolean(),
})

/**
 * Quality control form validation schema
 */
export const qualityControlFormSchema = z.object({
  delivery_id: z.string().min(1, 'Delivery ID is required'),
  inspector: z.string().min(1, 'Inspector is required'),
  check_date: z.string().min(1, 'Inspection date is required'),
  passed: z.boolean(),
  issues: z.string(),
  corrective_action: z.string(),
  status: qualityControlStatusSchema,
})

export type QualityControlFormData = z.infer<typeof qualityControlFormSchema>
export type ChecklistItemData = z.infer<typeof checklistItemSchema>

// ============================================
// DOCUMENT UPLOAD SCHEMAS
// ============================================

/**
 * Document category enum schema
 */
export const documentCategorySchema = z.enum([
  'Procedures',
  'Policies',
  'Training',
  'Reports',
  'Templates',
  'Other',
])

/**
 * Document upload form validation schema
 */
export const documentUploadFormSchema = z.object({
  doc_name: z.string().min(1, 'Document name is required'),
  category: z.string().min(1, 'Category is required'),
  version: z.string(),
  description: z.string(),
  tags: z.string(),
  file_url: z.string(),
})

export type DocumentUploadFormData = z.infer<typeof documentUploadFormSchema>

// ============================================
// HANDOVER SCHEMAS
// ============================================

/**
 * Handover form validation schema
 */
export const handoverFormSchema = z.object({
  from_courier: z.string().min(1, 'From courier is required'),
  to_courier: z.string().min(1, 'To courier is required'),
  vehicle_id: z.string(),
  handover_date: z.string().min(1, 'Handover date is required'),
  checklist: z.array(checklistItemSchema).optional(),
  notes: z.string(),
  signature: z.string(),
})

export type HandoverFormData = z.infer<typeof handoverFormSchema>

// ============================================
// EXPENSE SCHEMAS
// ============================================

/**
 * Expense category enum schema
 */
export const expenseCategorySchema = z.enum([
  'fuel',
  'maintenance',
  'equipment',
  'office',
  'travel',
  'utilities',
  'other',
])

/**
 * Expense status enum schema
 */
export const expenseStatusSchema = z.enum(['pending', 'approved', 'rejected'])

/**
 * Expense form validation schema
 */
export const expenseFormSchema = z.object({
  date: z.string().min(1, 'Date is required'),
  category: z.string().min(1, 'Category is required'),
  description: z.string().min(1, 'Description is required'),
  amount: z.number().positive('Amount must be greater than 0'),
  status: expenseStatusSchema,
  receipt_url: z.string(),
})

export type ExpenseFormData = z.infer<typeof expenseFormSchema>

// ============================================
// BUDGET SCHEMAS
// ============================================

/**
 * Budget department enum schema
 */
export const budgetDepartmentSchema = z.enum([
  'operations',
  'fleet',
  'hr',
  'finance',
  'it',
  'marketing',
  'admin',
])

/**
 * Budget category enum schema
 */
export const budgetCategorySchema = z.enum([
  'salary',
  'equipment',
  'maintenance',
  'fuel',
  'training',
  'supplies',
  'other',
])

/**
 * Budget form validation schema
 */
export const budgetFormSchema = z.object({
  department: z.string().min(1, 'Department is required'),
  category: z.string().min(1, 'Category is required'),
  allocated: z.number().nonnegative('Allocated amount cannot be negative'),
  spent: z.number().nonnegative(),
  period: z.string().min(1, 'Period is required'),
  notes: z.string(),
})

export type BudgetFormData = z.infer<typeof budgetFormSchema>

// ============================================
// PENALTY SCHEMAS (for formConfigs compatibility)
// ============================================

/**
 * Penalty reason enum schema
 */
export const penaltyReasonSchema = z.enum([
  'late',
  'no_show',
  'damage',
  'complaint',
  'other',
])

/**
 * Approval status enum schema
 */
export const approvalStatusSchema = z.enum(['pending', 'approved', 'rejected'])

/**
 * Penalty form validation schema (for formConfigs)
 */
export const penaltyFormConfigSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  date: z.string().min(1, 'Date is required'),
  reason: z.string().min(1, 'Reason is required'),
  amount: z.number().positive('Amount must be greater than 0'),
  status: approvalStatusSchema,
  notes: z.string(),
})

export type PenaltyFormConfigData = z.infer<typeof penaltyFormConfigSchema>

// ============================================
// BONUS SCHEMAS (for formConfigs compatibility)
// ============================================

/**
 * Bonus reason enum schema
 */
export const bonusReasonSchema = z.enum([
  'performance',
  'attendance',
  'special',
  'holiday',
  'other',
])

/**
 * Bonus form validation schema (for formConfigs)
 */
export const bonusFormConfigSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  month: z.string().min(1, 'Month is required'),
  amount: z.number().positive('Amount must be greater than 0'),
  reason: z.string().min(1, 'Reason is required'),
  status: approvalStatusSchema,
  notes: z.string(),
})

export type BonusFormConfigData = z.infer<typeof bonusFormConfigSchema>

// ============================================
// COURIER DOCUMENT SCHEMAS
// ============================================

/**
 * Document type enum schema
 */
export const courierDocumentTypeSchema = z.enum([
  'id',
  'license',
  'iqama',
  'insurance',
  'vehicle_registration',
  'health_certificate',
  'other',
])

/**
 * Document status enum schema
 */
export const courierDocumentStatusSchema = z.enum(['valid', 'expiring', 'expired'])

/**
 * Courier document form validation schema
 */
export const courierDocumentFormSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  document_type: z.string().min(1, 'Document type is required'),
  expiry_date: z.string(),
  status: courierDocumentStatusSchema,
  notes: z.string(),
  file_url: z.string(),
})

export type CourierDocumentFormConfigData = z.infer<typeof courierDocumentFormSchema>
