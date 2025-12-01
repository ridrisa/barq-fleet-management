import { FormConfig } from './DynamicForm'
import { ValidationSchema } from '@/hooks/useForm'
import { type ChecklistItem } from './ChecklistField'

// ============================================
// PENALTY FORM
// ============================================
export interface PenaltyFormData {
  courier_id: string
  date: string
  reason: string
  amount: number
  status: 'pending' | 'approved' | 'rejected'
  notes: string
}

export const penaltyFormConfig: FormConfig = {
  sections: [
    {
      title: 'Penalty Details',
      description: 'Record a penalty for a courier',
      fields: [
        { name: 'courier_id', label: 'Courier', type: 'select', required: true, placeholder: 'Select courier' },
        { name: 'date', label: 'Date', type: 'date', required: true },
        { name: 'reason', label: 'Reason', type: 'select', required: true, options: [
          { value: '', label: 'Select reason' },
          { value: 'late', label: 'Late Arrival' },
          { value: 'no_show', label: 'No Show' },
          { value: 'damage', label: 'Package Damage' },
          { value: 'complaint', label: 'Customer Complaint' },
          { value: 'other', label: 'Other' },
        ]},
        { name: 'amount', label: 'Amount (SAR)', type: 'number', required: true, placeholder: '0.00' },
        { name: 'status', label: 'Status', type: 'select', required: true, options: [
          { value: 'pending', label: 'Pending' },
          { value: 'approved', label: 'Approved' },
          { value: 'rejected', label: 'Rejected' },
        ]},
      ],
    },
    {
      title: 'Additional Information',
      fields: [
        { name: 'notes', label: 'Notes', type: 'textarea', placeholder: 'Additional details about this penalty...' },
      ],
    },
  ],
}

export const penaltyInitialData: PenaltyFormData = {
  courier_id: '',
  date: new Date().toISOString().split('T')[0],
  reason: '',
  amount: 0,
  status: 'pending',
  notes: '',
}

export const penaltyValidation: ValidationSchema<PenaltyFormData> = {
  courier_id: (data) => !data.courier_id ? 'Courier is required' : null,
  date: (data) => !data.date ? 'Date is required' : null,
  reason: (data) => !data.reason ? 'Reason is required' : null,
  amount: (data) => data.amount <= 0 ? 'Amount must be greater than 0' : null,
}

// ============================================
// BONUS FORM
// ============================================
export interface BonusFormData {
  courier_id: string
  month: string
  amount: number
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  notes: string
}

export const bonusFormConfig: FormConfig = {
  sections: [
    {
      title: 'Bonus Details',
      description: 'Award a bonus to a courier',
      fields: [
        { name: 'courier_id', label: 'Courier', type: 'select', required: true, placeholder: 'Select courier' },
        { name: 'month', label: 'Month', type: 'date', required: true },
        { name: 'amount', label: 'Amount (SAR)', type: 'number', required: true, placeholder: '0.00' },
        { name: 'reason', label: 'Reason', type: 'select', required: true, options: [
          { value: '', label: 'Select reason' },
          { value: 'performance', label: 'Performance Bonus' },
          { value: 'attendance', label: 'Perfect Attendance' },
          { value: 'special', label: 'Special Achievement' },
          { value: 'holiday', label: 'Holiday Bonus' },
          { value: 'other', label: 'Other' },
        ]},
        { name: 'status', label: 'Status', type: 'select', required: true, options: [
          { value: 'pending', label: 'Pending' },
          { value: 'approved', label: 'Approved' },
          { value: 'rejected', label: 'Rejected' },
        ]},
      ],
    },
    {
      title: 'Additional Information',
      fields: [
        { name: 'notes', label: 'Notes', type: 'textarea', placeholder: 'Additional details about this bonus...' },
      ],
    },
  ],
}

export const bonusInitialData: BonusFormData = {
  courier_id: '',
  month: new Date().toISOString().split('T')[0],
  amount: 0,
  reason: '',
  status: 'pending',
  notes: '',
}

export const bonusValidation: ValidationSchema<BonusFormData> = {
  courier_id: (data) => !data.courier_id ? 'Courier is required' : null,
  month: (data) => !data.month ? 'Month is required' : null,
  amount: (data) => data.amount <= 0 ? 'Amount must be greater than 0' : null,
  reason: (data) => !data.reason ? 'Reason is required' : null,
}

// ============================================
// EXPENSE FORM
// ============================================
export interface ExpenseFormData {
  date: string
  category: string
  description: string
  amount: number
  status: 'pending' | 'approved' | 'rejected'
  receipt_url: string
}

export const expenseFormConfig: FormConfig = {
  sections: [
    {
      title: 'Expense Details',
      description: 'Record a business expense',
      fields: [
        { name: 'date', label: 'Date', type: 'date', required: true },
        { name: 'category', label: 'Category', type: 'select', required: true, options: [
          { value: '', label: 'Select category' },
          { value: 'fuel', label: 'Fuel' },
          { value: 'maintenance', label: 'Maintenance' },
          { value: 'equipment', label: 'Equipment' },
          { value: 'office', label: 'Office Supplies' },
          { value: 'travel', label: 'Travel' },
          { value: 'utilities', label: 'Utilities' },
          { value: 'other', label: 'Other' },
        ]},
        { name: 'description', label: 'Description', type: 'text', required: true, placeholder: 'Brief description of expense' },
        { name: 'amount', label: 'Amount (SAR)', type: 'number', required: true, placeholder: '0.00' },
        { name: 'status', label: 'Status', type: 'select', required: true, options: [
          { value: 'pending', label: 'Pending' },
          { value: 'approved', label: 'Approved' },
          { value: 'rejected', label: 'Rejected' },
        ]},
      ],
    },
    {
      title: 'Documentation',
      fields: [
        { name: 'receipt_url', label: 'Receipt URL', type: 'text', placeholder: 'Link to receipt/invoice' },
      ],
    },
  ],
}

export const expenseInitialData: ExpenseFormData = {
  date: new Date().toISOString().split('T')[0],
  category: '',
  description: '',
  amount: 0,
  status: 'pending',
  receipt_url: '',
}

export const expenseValidation: ValidationSchema<ExpenseFormData> = {
  date: (data) => !data.date ? 'Date is required' : null,
  category: (data) => !data.category ? 'Category is required' : null,
  description: (data) => !data.description ? 'Description is required' : null,
  amount: (data) => data.amount <= 0 ? 'Amount must be greater than 0' : null,
}

// ============================================
// SERVICE LEVEL (SLA) FORM
// ============================================
export interface ServiceLevelFormData {
  service_type: string
  target_time: number
  time_unit: 'minutes' | 'hours' | 'days'
  measurement: string
  penalty_amount: number
  measurement_period: 'daily' | 'weekly' | 'monthly'
  is_active: boolean
}

export const serviceLevelFormConfig: FormConfig = {
  sections: [
    {
      title: 'SLA Definition',
      description: 'Define service level agreement parameters',
      fields: [
        { name: 'service_type', label: 'Service Type', type: 'select', required: true, options: [
          { value: '', label: 'Select service type' },
          { value: 'standard_delivery', label: 'Standard Delivery' },
          { value: 'express_delivery', label: 'Express Delivery' },
          { value: 'same_day', label: 'Same Day Delivery' },
          { value: 'next_day', label: 'Next Day Delivery' },
          { value: 'pickup', label: 'Pickup Service' },
          { value: 'returns', label: 'Returns Processing' },
        ]},
        { name: 'target_time', label: 'Target Time', type: 'number', required: true, placeholder: 'e.g., 24' },
        { name: 'time_unit', label: 'Time Unit', type: 'select', required: true, options: [
          { value: 'minutes', label: 'Minutes' },
          { value: 'hours', label: 'Hours' },
          { value: 'days', label: 'Days' },
        ]},
        { name: 'measurement', label: 'Measurement Method', type: 'text', placeholder: 'How is this SLA measured?' },
      ],
    },
    {
      title: 'Penalty & Period',
      fields: [
        { name: 'penalty_amount', label: 'Penalty Amount (SAR)', type: 'number', placeholder: 'Penalty for SLA breach' },
        { name: 'measurement_period', label: 'Measurement Period', type: 'select', options: [
          { value: 'daily', label: 'Daily' },
          { value: 'weekly', label: 'Weekly' },
          { value: 'monthly', label: 'Monthly' },
        ]},
        { name: 'is_active', label: 'Active', type: 'checkbox' },
      ],
    },
  ],
}

export const serviceLevelInitialData: ServiceLevelFormData = {
  service_type: '',
  target_time: 24,
  time_unit: 'hours',
  measurement: '',
  penalty_amount: 0,
  measurement_period: 'monthly',
  is_active: true,
}

export const serviceLevelValidation: ValidationSchema<ServiceLevelFormData> = {
  service_type: (data) => !data.service_type ? 'Service type is required' : null,
  target_time: (data) => data.target_time <= 0 ? 'Target time must be greater than 0' : null,
}

// ============================================
// BUDGET FORM
// ============================================
export interface BudgetFormData {
  department: string
  category: string
  allocated: number
  spent: number
  period: string
  notes: string
}

export const budgetFormConfig: FormConfig = {
  sections: [
    {
      title: 'Budget Allocation',
      description: 'Define budget for a department or category',
      fields: [
        { name: 'department', label: 'Department', type: 'select', required: true, options: [
          { value: '', label: 'Select department' },
          { value: 'operations', label: 'Operations' },
          { value: 'fleet', label: 'Fleet Management' },
          { value: 'hr', label: 'Human Resources' },
          { value: 'finance', label: 'Finance' },
          { value: 'it', label: 'IT' },
          { value: 'marketing', label: 'Marketing' },
          { value: 'admin', label: 'Administration' },
        ]},
        { name: 'category', label: 'Category', type: 'select', required: true, options: [
          { value: '', label: 'Select category' },
          { value: 'salary', label: 'Salaries' },
          { value: 'equipment', label: 'Equipment' },
          { value: 'maintenance', label: 'Maintenance' },
          { value: 'fuel', label: 'Fuel' },
          { value: 'training', label: 'Training' },
          { value: 'supplies', label: 'Supplies' },
          { value: 'other', label: 'Other' },
        ]},
        { name: 'period', label: 'Period', type: 'text', required: true, placeholder: 'e.g., Q1 2024' },
      ],
    },
    {
      title: 'Amounts',
      fields: [
        { name: 'allocated', label: 'Allocated Amount (SAR)', type: 'number', required: true, placeholder: '0.00' },
        { name: 'spent', label: 'Spent Amount (SAR)', type: 'number', placeholder: '0.00' },
        { name: 'notes', label: 'Notes', type: 'textarea', placeholder: 'Additional budget notes...' },
      ],
    },
  ],
}

export const budgetInitialData: BudgetFormData = {
  department: '',
  category: '',
  allocated: 0,
  spent: 0,
  period: '',
  notes: '',
}

export const budgetValidation: ValidationSchema<BudgetFormData> = {
  department: (data) => !data.department ? 'Department is required' : null,
  category: (data) => !data.category ? 'Category is required' : null,
  period: (data) => !data.period ? 'Period is required' : null,
  allocated: (data) => data.allocated < 0 ? 'Allocated amount cannot be negative' : null,
}

// ============================================
// COURIER DOCUMENT FORM
// ============================================
export interface CourierDocumentFormData {
  courier_id: string
  document_type: string
  expiry_date: string
  status: 'valid' | 'expiring' | 'expired'
  notes: string
  file_url?: string
}

export const courierDocumentFormConfig: FormConfig = {
  sections: [
    {
      title: 'Document Details',
      description: 'Upload and manage courier documents',
      fields: [
        { name: 'courier_id', label: 'Courier', type: 'select', required: true, placeholder: 'Select courier' },
        { name: 'document_type', label: 'Document Type', type: 'select', required: true, options: [
          { value: '', label: 'Select document type' },
          { value: 'id', label: 'National ID' },
          { value: 'license', label: 'Driving License' },
          { value: 'iqama', label: 'Iqama' },
          { value: 'insurance', label: 'Insurance' },
          { value: 'vehicle_registration', label: 'Vehicle Registration' },
          { value: 'health_certificate', label: 'Health Certificate' },
          { value: 'other', label: 'Other' },
        ]},
        { name: 'expiry_date', label: 'Expiry Date', type: 'date' },
        { name: 'status', label: 'Status', type: 'select', required: true, options: [
          { value: 'valid', label: 'Valid' },
          { value: 'expiring', label: 'Expiring Soon' },
          { value: 'expired', label: 'Expired' },
        ]},
      ],
    },
    {
      title: 'Additional Information',
      fields: [
        { name: 'notes', label: 'Notes', type: 'textarea', placeholder: 'Any additional notes about this document...' },
      ],
    },
  ],
}

export const courierDocumentInitialData: CourierDocumentFormData = {
  courier_id: '',
  document_type: '',
  expiry_date: '',
  status: 'valid',
  notes: '',
  file_url: '',
}

export const courierDocumentValidation: ValidationSchema<CourierDocumentFormData> = {
  courier_id: (data) => !data.courier_id ? 'Courier is required' : null,
  document_type: (data) => !data.document_type ? 'Document type is required' : null,
}

// ============================================
// QUALITY CONTROL FORM
// ============================================
export interface QualityControlFormData {
  delivery_id: string
  inspector: string
  check_date: string
  passed: boolean
  issues: string
  corrective_action: string
  status: 'pending' | 'in_progress' | 'completed'
}

export const qualityControlFormConfig: FormConfig = {
  sections: [
    {
      title: 'Inspection Details',
      description: 'Record quality control inspection',
      fields: [
        { name: 'delivery_id', label: 'Delivery ID', type: 'text', required: true, placeholder: 'Enter delivery ID' },
        { name: 'inspector', label: 'Inspector', type: 'select', required: true, placeholder: 'Select inspector' },
        { name: 'check_date', label: 'Inspection Date', type: 'date', required: true },
      ],
    },
    {
      title: 'Inspection Result',
      fields: [
        { name: 'passed', label: 'Passed Inspection', type: 'checkbox' },
        { name: 'issues', label: 'Issues Found', type: 'textarea', placeholder: 'Describe any issues found...' },
        { name: 'corrective_action', label: 'Corrective Action', type: 'textarea', placeholder: 'Actions to be taken...' },
        { name: 'status', label: 'Status', type: 'select', options: [
          { value: 'pending', label: 'Pending' },
          { value: 'in_progress', label: 'In Progress' },
          { value: 'completed', label: 'Completed' },
        ]},
      ],
    },
  ],
}

export const qualityControlInitialData: QualityControlFormData = {
  delivery_id: '',
  inspector: '',
  check_date: new Date().toISOString().split('T')[0],
  passed: false,
  issues: '',
  corrective_action: '',
  status: 'pending',
}

export const qualityControlValidation: ValidationSchema<QualityControlFormData> = {
  delivery_id: (data) => !data.delivery_id ? 'Delivery ID is required' : null,
  inspector: (data) => !data.inspector ? 'Inspector is required' : null,
  check_date: (data) => !data.check_date ? 'Inspection date is required' : null,
}

// ============================================
// INCIDENT REPORTING FORM
// ============================================
export interface IncidentReportFormData {
  title: string
  incident_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  location: string
  description: string
  status: 'open' | 'investigating' | 'resolved' | 'closed'
  reported_by: string
  evidence_urls: string[]
}

export const incidentFormConfig: FormConfig = {
  sections: [
    {
      title: 'Incident Details',
      description: 'Report an incident or issue',
      fields: [
        { name: 'title', label: 'Incident Title', type: 'text', required: true, placeholder: 'Brief title of the incident' },
        { name: 'incident_type', label: 'Incident Type', type: 'select', required: true, options: [
          { value: '', label: 'Select type' },
          { value: 'accident', label: 'Accident' },
          { value: 'theft', label: 'Theft' },
          { value: 'damage', label: 'Property Damage' },
          { value: 'complaint', label: 'Customer Complaint' },
          { value: 'injury', label: 'Injury' },
          { value: 'other', label: 'Other' },
        ]},
        { name: 'severity', label: 'Severity', type: 'select', required: true, options: [
          { value: 'low', label: 'Low' },
          { value: 'medium', label: 'Medium' },
          { value: 'high', label: 'High' },
          { value: 'critical', label: 'Critical' },
        ]},
        { name: 'location', label: 'Location', type: 'text', placeholder: 'Where did this occur?' },
      ],
    },
    {
      title: 'Description & Status',
      fields: [
        { name: 'description', label: 'Description', type: 'textarea', required: true, placeholder: 'Detailed description of what happened...' },
        { name: 'status', label: 'Status', type: 'select', options: [
          { value: 'open', label: 'Open' },
          { value: 'investigating', label: 'Investigating' },
          { value: 'resolved', label: 'Resolved' },
          { value: 'closed', label: 'Closed' },
        ]},
        { name: 'reported_by', label: 'Reported By', type: 'text', placeholder: 'Name of reporter' },
      ],
    },
  ],
}

export const incidentInitialData: IncidentReportFormData = {
  title: '',
  incident_type: '',
  severity: 'medium',
  location: '',
  description: '',
  status: 'open',
  reported_by: '',
  evidence_urls: [],
}

export const incidentValidation: ValidationSchema<IncidentReportFormData> = {
  title: (data) => !data.title ? 'Title is required' : null,
  incident_type: (data) => !data.incident_type ? 'Incident type is required' : null,
  description: (data) => !data.description ? 'Description is required' : null,
}

// ============================================
// DOCUMENT UPLOAD FORM
// ============================================
export interface DocumentUploadFormData {
  doc_name: string
  category: string
  version: string
  description: string
  tags: string
  file_url?: string
}

export const documentUploadFormConfig: FormConfig = {
  sections: [
    {
      title: 'Document Information',
      description: 'Upload a new document to the library',
      fields: [
        { name: 'doc_name', label: 'Document Name', type: 'text', required: true, placeholder: 'Enter document name' },
        { name: 'category', label: 'Category', type: 'select', required: true, options: [
          { value: '', label: 'Select category' },
          { value: 'Procedures', label: 'Procedures' },
          { value: 'Policies', label: 'Policies' },
          { value: 'Training', label: 'Training Materials' },
          { value: 'Reports', label: 'Reports' },
          { value: 'Templates', label: 'Templates' },
          { value: 'Other', label: 'Other' },
        ]},
        { name: 'version', label: 'Version', type: 'text', placeholder: 'e.g., 1.0' },
      ],
    },
    {
      title: 'Additional Details',
      fields: [
        { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Brief description of this document...' },
        { name: 'tags', label: 'Tags', type: 'text', placeholder: 'Comma-separated tags (e.g., safety, training)' },
      ],
    },
  ],
}

export const documentUploadInitialData: DocumentUploadFormData = {
  doc_name: '',
  category: '',
  version: '1.0',
  description: '',
  tags: '',
  file_url: '',
}

export const documentUploadValidation: ValidationSchema<DocumentUploadFormData> = {
  doc_name: (data) => !data.doc_name ? 'Document name is required' : null,
  category: (data) => !data.category ? 'Category is required' : null,
}

// ============================================
// HANDOVER FORM
// ============================================
export interface HandoverFormData {
  from_courier: string
  to_courier: string
  vehicle_id: string
  handover_date: string
  checklist: ChecklistItem[]
  notes: string
  signature?: string
}

export const defaultHandoverChecklist: ChecklistItem[] = [
  { id: '1', label: 'Vehicle keys handed over', checked: false },
  { id: '2', label: 'Vehicle condition verified', checked: false },
  { id: '3', label: 'Fuel level noted', checked: false },
  { id: '4', label: 'Documents transferred', checked: false },
  { id: '5', label: 'Pending deliveries briefed', checked: false },
  { id: '6', label: 'Equipment checked', checked: false },
  { id: '7', label: 'Cash/COD reconciled', checked: false },
]

export const handoverFormConfig: FormConfig = {
  sections: [
    {
      title: 'Handover Details',
      description: 'Record shift handover between couriers',
      fields: [
        { name: 'from_courier', label: 'From Courier', type: 'select', required: true, placeholder: 'Select courier' },
        { name: 'to_courier', label: 'To Courier', type: 'select', required: true, placeholder: 'Select courier' },
        { name: 'vehicle_id', label: 'Vehicle', type: 'select', placeholder: 'Select vehicle' },
        { name: 'handover_date', label: 'Handover Date', type: 'date', required: true },
      ],
    },
    {
      title: 'Notes',
      fields: [
        { name: 'notes', label: 'Additional Notes', type: 'textarea', placeholder: 'Any additional handover notes...' },
      ],
    },
  ],
}

export const handoverInitialData: HandoverFormData = {
  from_courier: '',
  to_courier: '',
  vehicle_id: '',
  handover_date: new Date().toISOString().split('T')[0],
  checklist: defaultHandoverChecklist,
  notes: '',
  signature: '',
}

export const handoverValidation: ValidationSchema<HandoverFormData> = {
  from_courier: (data) => !data.from_courier ? 'From courier is required' : null,
  to_courier: (data) => !data.to_courier ? 'To courier is required' : null,
  handover_date: (data) => !data.handover_date ? 'Handover date is required' : null,
}

// ============================================
// HELPER: Get courier options
// ============================================
export const getCourierOptions = (couriers: Array<{ id: string | number; name: string }>) => [
  { value: '', label: 'Select courier' },
  ...couriers.map(c => ({ value: String(c.id), label: c.name }))
]

export const getVehicleOptions = (vehicles: Array<{ id: string | number; plate_number: string }>) => [
  { value: '', label: 'Select vehicle' },
  ...vehicles.map(v => ({ value: String(v.id), label: v.plate_number }))
]

export const getUserOptions = (users: Array<{ id: string | number; full_name: string }>) => [
  { value: '', label: 'Select user' },
  ...users.map(u => ({ value: String(u.id), label: u.full_name }))
]
