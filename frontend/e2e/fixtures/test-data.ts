/**
 * E2E Test Data Fixtures
 *
 * Provides test data for E2E tests including:
 * - User credentials
 * - Sample courier data
 * - Sample vehicle data
 * - Sample delivery data
 *
 * Author: BARQ QA Team
 * Last Updated: 2025-12-06
 */

export const testUsers = {
  admin: {
    email: 'admin@barq.com',
    password: 'admin123',
    role: 'admin',
    fullName: 'Admin User',
  },
  manager: {
    email: 'manager@barq.com',
    password: 'manager123',
    role: 'manager',
    fullName: 'Manager User',
  },
  user: {
    email: 'user@barq.com',
    password: 'user123',
    role: 'user',
    fullName: 'Standard User',
  },
  invalid: {
    email: 'invalid@example.com',
    password: 'wrongpassword',
  },
}

export const testCouriers = {
  active: {
    barqId: 'BRQ-E2E-001',
    fullName: 'E2E Test Courier',
    email: 'e2e-courier@test.com',
    mobileNumber: '+966501234567',
    status: 'active',
    city: 'Riyadh',
    sponsorshipStatus: 'inhouse',
    projectType: 'barq',
  },
  inactive: {
    barqId: 'BRQ-E2E-002',
    fullName: 'Inactive Courier',
    email: 'inactive-courier@test.com',
    mobileNumber: '+966502234567',
    status: 'inactive',
    city: 'Jeddah',
    sponsorshipStatus: 'ajeer',
    projectType: 'ecommerce',
  },
  onLeave: {
    barqId: 'BRQ-E2E-003',
    fullName: 'On Leave Courier',
    email: 'onleave-courier@test.com',
    mobileNumber: '+966503234567',
    status: 'on_leave',
    city: 'Dammam',
    sponsorshipStatus: 'inhouse',
    projectType: 'food',
  },
}

export const testVehicles = {
  available: {
    plateNumber: 'E2E-001',
    vehicleType: 'motorcycle',
    make: 'Honda',
    model: 'Wave 110',
    year: 2023,
    status: 'available',
    city: 'Riyadh',
  },
  assigned: {
    plateNumber: 'E2E-002',
    vehicleType: 'motorcycle',
    make: 'Yamaha',
    model: 'FZ',
    year: 2023,
    status: 'assigned',
    city: 'Jeddah',
  },
  maintenance: {
    plateNumber: 'E2E-003',
    vehicleType: 'car',
    make: 'Toyota',
    model: 'Hiace',
    year: 2022,
    status: 'maintenance',
    city: 'Riyadh',
  },
}

export const testDeliveries = {
  pending: {
    trackingNumber: 'TRK-E2E-001',
    status: 'pending',
    pickupAddress: '123 Pickup St, Riyadh',
    deliveryAddress: '456 Delivery Ave, Riyadh',
    customerName: 'Test Customer',
    customerPhone: '+966509876543',
  },
  inProgress: {
    trackingNumber: 'TRK-E2E-002',
    status: 'in_transit',
    pickupAddress: '789 Pickup Blvd, Jeddah',
    deliveryAddress: '101 Delivery St, Jeddah',
    customerName: 'Another Customer',
    customerPhone: '+966508765432',
  },
  completed: {
    trackingNumber: 'TRK-E2E-003',
    status: 'delivered',
    pickupAddress: 'Warehouse A, Dammam',
    deliveryAddress: 'Customer Address, Dammam',
    customerName: 'Completed Customer',
    customerPhone: '+966507654321',
  },
}

export const testLeaveRequests = {
  annual: {
    type: 'annual',
    startDate: getDateOffset(7),
    endDate: getDateOffset(12),
    reason: 'Annual vacation',
  },
  sick: {
    type: 'sick',
    startDate: getDateOffset(0),
    endDate: getDateOffset(2),
    reason: 'Medical appointment',
  },
  emergency: {
    type: 'emergency',
    startDate: getDateOffset(0),
    endDate: getDateOffset(1),
    reason: 'Family emergency',
  },
}

/**
 * Get date string with offset from today
 */
function getDateOffset(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

/**
 * Generate random test data
 */
export const generators = {
  barqId: () => `BRQ-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
  email: () => `test-${Date.now()}@e2e.test`,
  phone: () => `+9665${Math.floor(10000000 + Math.random() * 90000000)}`,
  plateNumber: () => `E2E-${Math.random().toString(36).substr(2, 5).toUpperCase()}`,
  trackingNumber: () => `TRK-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
}

/**
 * API endpoints for E2E tests
 */
export const apiEndpoints = {
  auth: {
    login: '/api/v1/auth/login',
    logout: '/api/v1/auth/logout',
    refresh: '/api/v1/auth/refresh',
    me: '/api/v1/auth/me',
  },
  dashboard: {
    stats: '/api/v1/dashboard/stats',
    alerts: '/api/v1/dashboard/alerts',
    summary: '/api/v1/dashboard/summary',
  },
  fleet: {
    couriers: '/api/v1/fleet/couriers',
    vehicles: '/api/v1/fleet/vehicles',
    assignments: '/api/v1/fleet/assignments',
  },
  operations: {
    deliveries: '/api/v1/operations/deliveries',
    routes: '/api/v1/operations/routes',
    cod: '/api/v1/operations/cod',
  },
  hr: {
    leaves: '/api/v1/hr/leaves',
    attendance: '/api/v1/hr/attendance',
    salary: '/api/v1/hr/salary',
    loans: '/api/v1/hr/loans',
  },
}
