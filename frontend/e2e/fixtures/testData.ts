/**
 * Test Data Fixtures
 * Centralized test data for E2E tests
 */

export const testUsers = {
  admin: {
    email: 'admin@barq.com',
    password: 'admin123',
    role: 'admin',
  },
  manager: {
    email: 'manager@barq.com',
    password: 'manager123',
    role: 'manager',
  },
  hr: {
    email: 'hr@barq.com',
    password: 'hr123',
    role: 'hr',
  },
  finance: {
    email: 'finance@barq.com',
    password: 'finance123',
    role: 'finance',
  },
}

export const testCouriers = {
  newCourier: {
    name: 'Ahmed Hassan',
    email: 'ahmed.hassan@test.com',
    phone: '+966501234567',
    nationalId: '1234567890',
    nationality: 'Saudi',
    dateOfBirth: '1990-01-01',
    city: 'Riyadh',
    project: 'Jahez',
  },
  updateCourier: {
    name: 'Ahmed Hassan Updated',
    phone: '+966509876543',
    city: 'Jeddah',
  },
}

export const testVehicles = {
  newVehicle: {
    plateNumber: 'ABC-1234',
    make: 'Toyota',
    model: 'Corolla',
    year: '2022',
    color: 'White',
    vin: 'JTDKB20U897654321',
    registrationExpiry: '2025-12-31',
    insuranceExpiry: '2025-06-30',
  },
  updateVehicle: {
    color: 'Silver',
    registrationExpiry: '2026-12-31',
  },
}

export const testWorkflows = {
  leaveRequest: {
    type: 'leave',
    title: 'Annual Leave Request',
    startDate: '2025-02-01',
    endDate: '2025-02-05',
    reason: 'Family vacation',
    notes: 'Planning a family trip',
  },
  loanRequest: {
    type: 'loan',
    title: 'Emergency Loan Request',
    amount: '5000',
    reason: 'Medical emergency',
    installments: '6',
  },
  courierOnboarding: {
    type: 'onboarding',
    title: 'New Courier Onboarding',
    courierName: 'Mohammed Ali',
    project: 'Jahez',
    startDate: '2025-02-01',
  },
}

export const testAssets = {
  newAsset: {
    name: 'Delivery Bag',
    type: 'equipment',
    serialNumber: 'BAG-001',
    value: '150',
    assignedTo: '',
  },
}

export const testLoans = {
  newLoan: {
    courierId: '',
    amount: '3000',
    installments: '6',
    reason: 'Personal emergency',
    startDate: '2025-02-01',
  },
}

export const testLeaves = {
  newLeave: {
    courierId: '',
    leaveType: 'annual',
    startDate: '2025-03-01',
    endDate: '2025-03-05',
    reason: 'Personal reasons',
    notes: 'Planned leave',
  },
}

export const testAccidents = {
  newAccident: {
    vehicleId: '',
    courierId: '',
    date: '2025-01-15',
    location: 'Riyadh - King Fahd Road',
    description: 'Minor collision with parked vehicle',
    severity: 'minor',
    estimatedCost: '2500',
  },
}

export const testVehicleLogs = {
  newLog: {
    vehicleId: '',
    type: 'maintenance',
    date: '2025-01-20',
    mileage: '45000',
    description: 'Regular oil change and filter replacement',
    cost: '250',
    serviceProvider: 'Quick Service Center',
  },
}

export const searchQueries = {
  courier: 'Ahmed',
  vehicle: 'ABC',
  workflow: 'leave',
  asset: 'bag',
  loan: 'emergency',
}

export const filterOptions = {
  status: {
    active: 'active',
    inactive: 'inactive',
    pending: 'pending',
    approved: 'approved',
    rejected: 'rejected',
    completed: 'completed',
  },
  leaveType: {
    annual: 'annual',
    sick: 'sick',
    emergency: 'emergency',
    unpaid: 'unpaid',
  },
  workflowType: {
    leave: 'leave',
    loan: 'loan',
    onboarding: 'onboarding',
    transfer: 'transfer',
  },
}

export const paginationTestData = {
  itemsPerPage: [10, 20, 50, 100],
  defaultPage: 1,
}

export const apiEndpoints = {
  login: '/api/auth/login',
  logout: '/api/auth/logout',
  couriers: '/api/couriers',
  vehicles: '/api/vehicles',
  workflows: '/api/workflows',
  leaves: '/api/leaves',
  loans: '/api/loans',
  assets: '/api/assets',
  accidents: '/api/accidents',
  vehicleLogs: '/api/vehicle-logs',
}

export const expectedResponseTimes = {
  pageLoad: 3000, // 3 seconds
  apiCall: 2000, // 2 seconds
  search: 1000, // 1 second
  filter: 500, // 500ms
}

export const validationMessages = {
  required: /required|cannot be empty|must be provided/i,
  invalidEmail: /invalid email|email format/i,
  invalidPhone: /invalid phone|phone format/i,
  invalidDate: /invalid date|date format/i,
}
