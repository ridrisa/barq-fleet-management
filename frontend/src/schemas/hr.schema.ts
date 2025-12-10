import { z } from 'zod'

/**
 * Leave type enum schema
 */
export const leaveTypeSchema = z.enum([
  'annual',
  'sick',
  'emergency',
  'unpaid',
  'maternity',
  'paternity',
  'bereavement',
  'hajj',
])

/**
 * Leave status enum schema
 */
export const leaveStatusSchema = z.enum([
  'pending',
  'approved',
  'rejected',
  'cancelled',
])

/**
 * Leave request form validation schema
 */
export const leaveRequestSchema = z.object({
  leave_type: leaveTypeSchema,
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  reason: z.string().min(10, 'Please provide a detailed reason').max(1000),
  emergency_contact: z
    .string()
    .regex(/^\+?[\d\s\-()]{8,20}$/, 'Invalid phone format')
    .optional()
    .or(z.literal('')),
  attachment_url: z.string().url().optional().or(z.literal('')),
}).refine(
  (data) => new Date(data.end_date) >= new Date(data.start_date),
  {
    message: 'End date must be after start date',
    path: ['end_date'],
  }
)

export type LeaveRequestFormData = z.infer<typeof leaveRequestSchema>

/**
 * Loan type enum schema
 */
export const loanTypeSchema = z.enum([
  'salary_advance',
  'personal',
  'emergency',
  'housing',
  'vehicle',
])

/**
 * Loan status enum schema
 */
export const loanStatusSchema = z.enum([
  'pending',
  'approved',
  'rejected',
  'active',
  'paid',
  'defaulted',
])

/**
 * Loan request form validation schema
 */
export const loanRequestSchema = z.object({
  loan_type: loanTypeSchema,
  amount: z
    .number()
    .positive('Amount must be positive')
    .max(100000, 'Amount exceeds maximum limit'),
  installments: z
    .number()
    .int()
    .min(1, 'At least 1 installment required')
    .max(24, 'Maximum 24 installments allowed'),
  reason: z.string().min(10, 'Please provide a detailed reason').max(1000),
  start_date: z.string().min(1, 'Start date is required'),
  guarantor_name: z.string().max(100).optional(),
  guarantor_phone: z
    .string()
    .regex(/^\+?[\d\s\-()]{8,20}$/, 'Invalid phone format')
    .optional()
    .or(z.literal('')),
})

export type LoanRequestFormData = z.infer<typeof loanRequestSchema>

/**
 * Salary component enum schema
 */
export const salaryComponentSchema = z.enum([
  'basic',
  'housing',
  'transportation',
  'food',
  'overtime',
  'bonus',
  'commission',
  'deduction',
])

/**
 * Salary record schema
 */
export const salaryRecordSchema = z.object({
  courier_id: z.number().int().positive('Courier is required'),
  month: z.number().int().min(1).max(12),
  year: z.number().int().min(2020).max(2100),
  basic_salary: z.number().nonnegative(),
  housing_allowance: z.number().nonnegative(),
  transportation_allowance: z.number().nonnegative(),
  food_allowance: z.number().nonnegative(),
  overtime_hours: z.number().nonnegative(),
  overtime_rate: z.number().nonnegative(),
  bonus: z.number().nonnegative(),
  commission: z.number().nonnegative(),
  deductions: z.number().nonnegative(),
  loan_deduction: z.number().nonnegative(),
  gosi_deduction: z.number().nonnegative(),
  notes: z.string().max(500),
})

export type SalaryRecordFormData = z.infer<typeof salaryRecordSchema>

/**
 * Attendance record schema
 */
export const attendanceRecordSchema = z.object({
  courier_id: z.number().int().positive('Courier is required'),
  date: z.string().min(1, 'Date is required'),
  check_in: z.string().optional(),
  check_out: z.string().optional(),
  status: z.enum(['present', 'absent', 'late', 'half_day', 'on_leave']),
  location: z.object({
    latitude: z.number().min(-90).max(90),
    longitude: z.number().min(-180).max(180),
  }).optional(),
  notes: z.string().max(500).optional(),
})

export type AttendanceRecordFormData = z.infer<typeof attendanceRecordSchema>

/**
 * Penalty type enum schema
 */
export const penaltyTypeSchema = z.enum([
  'late_arrival',
  'absence',
  'misconduct',
  'damage',
  'violation',
  'customer_complaint',
  'policy_breach',
])

/**
 * Penalty record schema
 */
export const penaltySchema = z.object({
  courier_id: z.number().int().positive('Courier is required'),
  penalty_type: penaltyTypeSchema,
  amount: z.number().nonnegative('Amount cannot be negative'),
  date: z.string().min(1, 'Date is required'),
  reason: z.string().min(10, 'Please provide a detailed reason').max(1000),
  reference_id: z.string().max(50).optional(),
  deduct_from_salary: z.boolean().optional().default(true),
})

export type PenaltyFormData = z.infer<typeof penaltySchema>

/**
 * Bonus record schema
 */
export const bonusSchema = z.object({
  courier_id: z.number().int().positive('Courier is required'),
  bonus_type: z.enum([
    'performance',
    'attendance',
    'referral',
    'holiday',
    'special',
    'retention',
  ]),
  amount: z.number().positive('Amount must be positive'),
  date: z.string().min(1, 'Date is required'),
  reason: z.string().min(5, 'Please provide a reason').max(500),
  add_to_salary: z.boolean().optional().default(true),
})

export type BonusFormData = z.infer<typeof bonusSchema>

/**
 * End of Service (EOS) calculation schema
 */
export const eosCalculationSchema = z.object({
  courier_id: z.number().int().positive('Courier is required'),
  termination_date: z.string().min(1, 'Termination date is required'),
  termination_reason: z.enum([
    'resignation',
    'termination',
    'contract_end',
    'retirement',
    'death',
  ]),
  final_basic_salary: z.number().positive('Basic salary is required'),
  unpaid_leave_days: z.number().int().nonnegative(),
  pending_loan_amount: z.number().nonnegative(),
  other_deductions: z.number().nonnegative(),
  notes: z.string().max(1000),
})

export type EOSCalculationFormData = z.infer<typeof eosCalculationSchema>
