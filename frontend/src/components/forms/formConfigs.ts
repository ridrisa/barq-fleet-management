import { z } from 'zod'
import { FormConfig } from './DynamicForm'
import { type ChecklistItem } from './ChecklistField'

// ============================================
// PENALTY FORM
// ============================================
export const penaltyFormSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  date: z.string().min(1, 'Date is required'),
  reason: z.string().min(1, 'Reason is required'),
  amount: z.number().positive('Amount must be greater than 0'),
  status: z.enum(['pending', 'approved', 'rejected']).default('pending'),
  notes: z.string().optional().default(''),
})

export type PenaltyFormData = z.infer<typeof penaltyFormSchema>

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

// ============================================
// BONUS FORM
// ============================================
export const bonusFormSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  month: z.string().min(1, 'Month is required'),
  amount: z.number().positive('Amount must be greater than 0'),
  reason: z.string().min(1, 'Reason is required'),
  status: z.enum(['pending', 'approved', 'rejected']).default('pending'),
  notes: z.string().optional().default(''),
})

export type BonusFormData = z.infer<typeof bonusFormSchema>

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

// ============================================
// EXPENSE FORM
// ============================================
export const expenseFormSchema = z.object({
  date: z.string().min(1, 'Date is required'),
  category: z.string().min(1, 'Category is required'),
  description: z.string().min(1, 'Description is required'),
  amount: z.number().positive('Amount must be greater than 0'),
  status: z.enum(['pending', 'approved', 'rejected']).default('pending'),
  receipt_url: z.string().optional().default(''),
})

export type ExpenseFormData = z.infer<typeof expenseFormSchema>

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

// ============================================
// SERVICE LEVEL (SLA) FORM
// ============================================
export const serviceLevelFormSchema = z.object({
  service_type: z.string().min(1, 'Service type is required'),
  target_time: z.number().positive('Target time must be greater than 0'),
  time_unit: z.enum(['minutes', 'hours', 'days']).default('hours'),
  measurement: z.string().optional().default(''),
  penalty_amount: z.number().nonnegative().optional().default(0),
  measurement_period: z.enum(['daily', 'weekly', 'monthly']).default('monthly'),
  is_active: z.boolean().optional().default(true),
})

export type ServiceLevelFormData = z.infer<typeof serviceLevelFormSchema>

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

// ============================================
// BUDGET FORM
// ============================================
export const budgetFormSchema = z.object({
  department: z.string().min(1, 'Department is required'),
  category: z.string().min(1, 'Category is required'),
  allocated: z.number().nonnegative('Allocated amount cannot be negative'),
  spent: z.number().nonnegative().optional().default(0),
  period: z.string().min(1, 'Period is required'),
  notes: z.string().optional().default(''),
})

export type BudgetFormData = z.infer<typeof budgetFormSchema>

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

// ============================================
// COURIER DOCUMENT FORM
// ============================================
export const courierDocumentFormSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  document_type: z.string().min(1, 'Document type is required'),
  expiry_date: z.string().optional().default(''),
  status: z.enum(['valid', 'expiring', 'expired']).default('valid'),
  notes: z.string().optional().default(''),
  file_url: z.string().optional().default(''),
})

export type CourierDocumentFormData = z.infer<typeof courierDocumentFormSchema>

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

// ============================================
// QUALITY CONTROL FORM
// ============================================
export const qualityControlFormSchema = z.object({
  delivery_id: z.string().min(1, 'Delivery ID is required'),
  inspector: z.string().min(1, 'Inspector is required'),
  check_date: z.string().min(1, 'Inspection date is required'),
  passed: z.boolean().optional().default(false),
  issues: z.string().optional().default(''),
  corrective_action: z.string().optional().default(''),
  status: z.enum(['pending', 'in_progress', 'completed']).default('pending'),
})

export type QualityControlFormData = z.infer<typeof qualityControlFormSchema>

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

// ============================================
// INCIDENT REPORTING FORM
// ============================================
export const incidentFormSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  incident_type: z.string().min(1, 'Incident type is required'),
  severity: z.enum(['low', 'medium', 'high', 'critical']).default('medium'),
  location: z.string().optional().default(''),
  description: z.string().min(1, 'Description is required'),
  status: z.enum(['open', 'investigating', 'resolved', 'closed']).default('open'),
  reported_by: z.string().optional().default(''),
  evidence_urls: z.array(z.string()).optional().default([]),
})

export type IncidentReportFormData = z.infer<typeof incidentFormSchema>

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

// ============================================
// DOCUMENT UPLOAD FORM
// ============================================
export const documentUploadFormSchema = z.object({
  doc_name: z.string().min(1, 'Document name is required'),
  category: z.string().min(1, 'Category is required'),
  version: z.string().optional().default('1.0'),
  description: z.string().optional().default(''),
  tags: z.string().optional().default(''),
  file_url: z.string().optional().default(''),
})

export type DocumentUploadFormData = z.infer<typeof documentUploadFormSchema>

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

// ============================================
// HANDOVER FORM
// ============================================
export const handoverFormSchema = z.object({
  from_courier: z.string().min(1, 'From courier is required'),
  to_courier: z.string().min(1, 'To courier is required'),
  vehicle_id: z.string().optional().default(''),
  handover_date: z.string().min(1, 'Handover date is required'),
  checklist: z.array(z.object({
    id: z.string(),
    label: z.string(),
    checked: z.boolean(),
  })).optional(),
  notes: z.string().optional().default(''),
  signature: z.string().optional().default(''),
})

export type HandoverFormData = z.infer<typeof handoverFormSchema>

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

// ============================================
// HELPER: Get options
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
