import { z } from 'zod'

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
  'insurance',
  'rent',
  'salary',
  'other',
])

/**
 * Expense status enum schema
 */
export const expenseStatusSchema = z.enum([
  'pending',
  'approved',
  'rejected',
  'reimbursed',
])

/**
 * Expense form validation schema
 */
export const expenseSchema = z.object({
  date: z.string().min(1, 'Date is required'),
  category: expenseCategorySchema,
  description: z.string().min(5, 'Description must be at least 5 characters').max(500),
  amount: z.number().positive('Amount must be greater than 0'),
  vendor: z.string().max(100),
  invoice_number: z.string().max(50),
  status: expenseStatusSchema,
  receipt_url: z.string(),
  notes: z.string().max(500),
})

export type ExpenseFormData = z.infer<typeof expenseSchema>

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
  'logistics',
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
  'travel',
  'utilities',
  'other',
])

/**
 * Budget form validation schema
 */
export const budgetSchema = z.object({
  department: budgetDepartmentSchema,
  category: budgetCategorySchema,
  period: z.string().min(1, 'Period is required'),
  fiscal_year: z.number().int().min(2020).max(2100),
  allocated: z.number().nonnegative('Allocated amount cannot be negative'),
  spent: z.number().nonnegative(),
  remaining: z.number().optional(),
  notes: z.string().max(500),
})

export type BudgetFormData = z.infer<typeof budgetSchema>

/**
 * Payroll status enum schema
 */
export const payrollStatusSchema = z.enum([
  'draft',
  'pending_approval',
  'approved',
  'processing',
  'paid',
  'cancelled',
])

/**
 * Payroll run form validation schema
 * Used for configuring payroll processing parameters
 */
export const payrollRunSchema = z.object({
  month: z.string().min(1, 'Month is required'),
  pay_date: z.string().min(1, 'Pay date is required'),
  include_bonuses: z.boolean(),
  include_deductions: z.boolean(),
  include_overtime: z.boolean(),
  notes: z.string().max(500),
})

export type PayrollRunFormData = z.infer<typeof payrollRunSchema>

/**
 * Individual payroll record schema
 */
export const payrollRecordSchema = z.object({
  employee_id: z.number().int().positive('Employee is required'),
  month: z.string().min(1, 'Month is required'),
  base_salary: z.number().nonnegative('Base salary cannot be negative'),
  housing_allowance: z.number().nonnegative(),
  transport_allowance: z.number().nonnegative(),
  mobile_allowance: z.number().nonnegative(),
  food_allowance: z.number().nonnegative(),
  other_allowances: z.number().nonnegative(),
  overtime_hours: z.number().nonnegative(),
  overtime_rate: z.number().positive(),
  bonus: z.number().nonnegative(),
  gosi_deduction: z.number().nonnegative(),
  loan_deduction: z.number().nonnegative(),
  penalty_deduction: z.number().nonnegative(),
  other_deductions: z.number().nonnegative(),
  status: payrollStatusSchema,
  notes: z.string().max(500),
})

export type PayrollRecordFormData = z.infer<typeof payrollRecordSchema>

/**
 * GOSI (Saudi Social Insurance) contribution schema
 */
export const gosiContributionSchema = z.object({
  employee_id: z.number().int().positive('Employee is required'),
  month: z.string().min(1, 'Month is required'),
  base_salary: z.number().positive('Base salary is required'),
  employee_rate: z.number().min(0).max(100),
  employer_rate: z.number().min(0).max(100),
  employee_contribution: z.number().nonnegative(),
  employer_contribution: z.number().nonnegative(),
  total_contribution: z.number().nonnegative(),
  is_saudi: z.boolean(),
  notes: z.string().max(500),
})

export type GOSIContributionFormData = z.infer<typeof gosiContributionSchema>

/**
 * GOSI batch processing schema
 */
export const gosiBatchSchema = z.object({
  month: z.string().min(1, 'Month is required'),
  include_saudis: z.boolean(),
  include_non_saudis: z.boolean(),
  employee_rate: z.number().min(0).max(100),
  employer_rate: z.number().min(0).max(100),
})

export type GOSIBatchFormData = z.infer<typeof gosiBatchSchema>

/**
 * Financial report type enum schema
 */
export const financialReportTypeSchema = z.enum([
  'income_statement',
  'balance_sheet',
  'cash_flow',
  'expense_report',
  'budget_variance',
  'payroll_summary',
  'gosi_summary',
])

/**
 * Report grouping enum schema
 */
export const reportGroupingSchema = z.enum([
  'day',
  'week',
  'month',
  'quarter',
  'year',
])

/**
 * Financial report configuration schema
 */
export const financialReportSchema = z.object({
  report_type: financialReportTypeSchema,
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  group_by: reportGroupingSchema,
  department: budgetDepartmentSchema.optional(),
  category: z.string(),
  include_projections: z.boolean(),
  compare_previous_period: z.boolean(),
  notes: z.string().max(500),
}).refine(
  (data) => new Date(data.end_date) >= new Date(data.start_date),
  {
    message: 'End date must be after start date',
    path: ['end_date'],
  }
)

export type FinancialReportFormData = z.infer<typeof financialReportSchema>

/**
 * Invoice status enum schema
 */
export const invoiceStatusSchema = z.enum([
  'draft',
  'sent',
  'paid',
  'overdue',
  'cancelled',
])

/**
 * Invoice schema
 */
export const invoiceSchema = z.object({
  invoice_number: z.string().min(1, 'Invoice number is required'),
  client_name: z.string().min(1, 'Client name is required'),
  client_email: z.string().email('Invalid email format').or(z.literal('')),
  issue_date: z.string().min(1, 'Issue date is required'),
  due_date: z.string().min(1, 'Due date is required'),
  subtotal: z.number().nonnegative(),
  tax_rate: z.number().min(0).max(100),
  tax_amount: z.number().nonnegative(),
  total: z.number().nonnegative(),
  status: invoiceStatusSchema,
  notes: z.string().max(1000),
})

export type InvoiceFormData = z.infer<typeof invoiceSchema>
