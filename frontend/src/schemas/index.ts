/**
 * BARQ Fleet Management - Zod Validation Schemas
 *
 * Centralized validation schemas using Zod for type-safe form validation.
 * Use with react-hook-form and @hookform/resolvers for seamless integration.
 *
 * @example
 * ```typescript
 * import { useForm } from 'react-hook-form';
 * import { zodResolver } from '@hookform/resolvers/zod';
 * import { courierSchema, CourierFormData } from '@/schemas';
 *
 * const { register, handleSubmit, formState: { errors } } = useForm<CourierFormData>({
 *   resolver: zodResolver(courierSchema),
 * });
 * ```
 */

// Courier schemas
export {
  courierSchema,
  courierStatusSchema,
  courierFilterSchema,
  courierDocumentSchema,
  type CourierFormData,
  type CourierFilterData,
  type CourierDocumentData,
} from './courier.schema'

// Vehicle schemas
export {
  vehicleSchema,
  vehicleTypeSchema,
  fuelTypeSchema,
  ownershipSchema,
  vehicleStatusSchema,
  vehicleFilterSchema,
  vehicleAssignmentSchema,
  maintenanceSchema,
  type VehicleFormData,
  type VehicleFilterData,
  type VehicleAssignmentData,
  type MaintenanceFormData,
} from './vehicle.schema'

// Auth schemas
export {
  loginSchema,
  registerSchema,
  forgotPasswordSchema,
  resetPasswordSchema,
  changePasswordSchema,
  userProfileSchema,
  userRoleSchema,
  type LoginFormData,
  type RegisterFormData,
  type ForgotPasswordFormData,
  type ResetPasswordFormData,
  type ChangePasswordFormData,
  type UserProfileFormData,
} from './auth.schema'

// Delivery schemas
export {
  deliverySchema,
  deliveryStatusSchema,
  deliveryPrioritySchema,
  deliveryFilterSchema,
  deliveryStatusUpdateSchema,
  bulkAssignmentSchema,
  addressSchema,
  contactSchema,
  packageSchema,
  type DeliveryFormData,
  type DeliveryFilterData,
  type DeliveryStatusUpdateData,
  type BulkAssignmentData,
  type AddressFormData,
  type ContactFormData,
  type PackageFormData,
} from './delivery.schema'

// HR schemas
export {
  leaveRequestSchema,
  leaveTypeSchema,
  leaveStatusSchema,
  loanRequestSchema,
  loanTypeSchema,
  loanStatusSchema,
  salaryRecordSchema,
  salaryComponentSchema,
  attendanceRecordSchema,
  penaltySchema,
  penaltyTypeSchema,
  bonusSchema,
  eosCalculationSchema,
  type LeaveRequestFormData,
  type LoanRequestFormData,
  type SalaryRecordFormData,
  type AttendanceRecordFormData,
  type PenaltyFormData,
  type BonusFormData,
  type EOSCalculationFormData,
} from './hr.schema'

// Finance schemas
export {
  expenseSchema,
  expenseCategorySchema as financeExpenseCategorySchema,
  expenseStatusSchema as financeExpenseStatusSchema,
  budgetSchema,
  budgetDepartmentSchema as financeBudgetDepartmentSchema,
  budgetCategorySchema as financeBudgetCategorySchema,
  payrollRunSchema,
  payrollRecordSchema,
  payrollStatusSchema,
  gosiContributionSchema,
  gosiBatchSchema,
  financialReportSchema,
  financialReportTypeSchema,
  reportGroupingSchema,
  invoiceSchema,
  invoiceStatusSchema,
  type ExpenseFormData as FinanceExpenseFormData,
  type BudgetFormData as FinanceBudgetFormData,
  type PayrollRunFormData,
  type PayrollRecordFormData,
  type GOSIContributionFormData,
  type GOSIBatchFormData,
  type FinancialReportFormData,
  type InvoiceFormData,
} from './finance.schema'

// Admin schemas
export {
  userRoleAdminSchema,
  userFormSchema,
  userCreateSchema,
  userEditSchema,
  assetTypeSchema,
  assetConditionSchema,
  assetStatusSchema,
  assetFormSchema,
  allocationStatusSchema,
  allocationFormSchema,
  buildingStatusSchema,
  buildingFormSchema,
  type UserFormData as AdminUserFormData,
  type UserCreateFormData,
  type UserEditFormData,
  type AssetFormData,
  type AllocationFormData,
  type BuildingFormData,
} from './admin.schema'

// Workflow schemas
export {
  workflowCategorySchema,
  workflowStatusSchema,
  workflowTriggerTypeSchema,
  workflowTemplateFormSchema,
  workflowInstanceStatusSchema,
  workflowInstanceSchema,
  type WorkflowTemplateFormData,
  type WorkflowInstanceFormData,
} from './workflow.schema'

// Operations schemas
export {
  slaTimeUnitSchema,
  slaMeasurementPeriodSchema,
  serviceLevelFormSchema,
  incidentSeveritySchema,
  incidentStatusSchema,
  incidentTypeSchema,
  incidentFormSchema,
  qualityControlStatusSchema,
  checklistItemSchema,
  qualityControlFormSchema,
  documentCategorySchema,
  documentUploadFormSchema,
  handoverFormSchema,
  expenseCategorySchema,
  expenseStatusSchema,
  expenseFormSchema,
  budgetDepartmentSchema,
  budgetCategorySchema,
  budgetFormSchema,
  penaltyReasonSchema,
  approvalStatusSchema,
  penaltyFormConfigSchema,
  bonusReasonSchema,
  bonusFormConfigSchema,
  courierDocumentTypeSchema,
  courierDocumentStatusSchema,
  courierDocumentFormSchema,
  type ServiceLevelFormData,
  type IncidentReportFormData,
  type QualityControlFormData,
  type ChecklistItemData,
  type DocumentUploadFormData,
  type HandoverFormData,
  type ExpenseFormData,
  type BudgetFormData,
  type PenaltyFormConfigData,
  type BonusFormConfigData,
  type CourierDocumentFormConfigData,
} from './operations.schema'
