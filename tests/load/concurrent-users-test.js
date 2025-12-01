/**
 * K6 Load Test: Concurrent Users Simulation
 * Simulates realistic user behavior patterns
 */

import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js'

export const options = {
  stages: [
    { duration: '2m', target: 50 },    // Morning rush
    { duration: '5m', target: 100 },   // Peak hours
    { duration: '2m', target: 150 },   // Lunch spike
    { duration: '5m', target: 100 },   // Afternoon
    { duration: '2m', target: 50 },    // Evening slowdown
    { duration: '1m', target: 0 },     // Night
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
}

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3003'
const API_BASE = `${BASE_URL}/api`

const USER_SCENARIOS = [
  'dashboard_viewer',
  'courier_manager',
  'fleet_supervisor',
  'hr_officer',
  'workflow_approver',
]

function authenticate() {
  const loginRes = http.post(`${API_BASE}/auth/login`, JSON.stringify({
    email: 'admin@barq.com',
    password: 'admin123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  })

  return loginRes.json('token') || null
}

function dashboardViewer(headers) {
  group('Dashboard Viewer', () => {
    http.get(`${API_BASE}/v1/dashboard/stats`, { headers })
    sleep(randomIntBetween(2, 5))

    http.get(`${API_BASE}/v1/dashboard/charts`, { headers })
    sleep(randomIntBetween(3, 8))
  })
}

function courierManager(headers) {
  group('Courier Manager', () => {
    // View couriers
    http.get(`${API_BASE}/v1/couriers`, { headers })
    sleep(randomIntBetween(1, 3))

    // Search courier
    http.get(`${API_BASE}/v1/couriers?search=ahmed`, { headers })
    sleep(randomIntBetween(1, 2))

    // View courier details
    http.get(`${API_BASE}/v1/couriers/1`, { headers })
    sleep(randomIntBetween(2, 5))
  })
}

function fleetSupervisor(headers) {
  group('Fleet Supervisor', () => {
    // View vehicles
    http.get(`${API_BASE}/v1/vehicles`, { headers })
    sleep(randomIntBetween(1, 3))

    // View assignments
    http.get(`${API_BASE}/v1/assignments`, { headers })
    sleep(randomIntBetween(2, 4))

    // View vehicle logs
    http.get(`${API_BASE}/v1/vehicle-logs`, { headers })
    sleep(randomIntBetween(2, 5))
  })
}

function hrOfficer(headers) {
  group('HR Officer', () => {
    // View salary
    http.get(`${API_BASE}/v1/hr/salary`, { headers })
    sleep(randomIntBetween(2, 4))

    // View attendance
    http.get(`${API_BASE}/v1/hr/attendance`, { headers })
    sleep(randomIntBetween(1, 3))

    // View loans
    http.get(`${API_BASE}/v1/hr/loans`, { headers })
    sleep(randomIntBetween(2, 5))
  })
}

function workflowApprover(headers) {
  group('Workflow Approver', () => {
    // View pending workflows
    http.get(`${API_BASE}/v1/workflows?status=pending`, { headers })
    sleep(randomIntBetween(2, 5))

    // View workflow details
    http.get(`${API_BASE}/v1/workflows/1`, { headers })
    sleep(randomIntBetween(3, 7))
  })
}

export default function () {
  const token = authenticate()
  if (!token) return

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  }

  // Randomly select user scenario
  const scenario = randomItem(USER_SCENARIOS)

  switch (scenario) {
    case 'dashboard_viewer':
      dashboardViewer(headers)
      break
    case 'courier_manager':
      courierManager(headers)
      break
    case 'fleet_supervisor':
      fleetSupervisor(headers)
      break
    case 'hr_officer':
      hrOfficer(headers)
      break
    case 'workflow_approver':
      workflowApprover(headers)
      break
  }

  sleep(randomIntBetween(1, 3))
}
