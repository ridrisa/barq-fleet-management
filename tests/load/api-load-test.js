/**
 * K6 Load Test: API Endpoints
 * Tests API performance under various load conditions
 */

import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { Rate, Trend, Counter } from 'k6/metrics'

// Custom metrics
const errorRate = new Rate('errors')
const apiDuration = new Trend('api_duration')
const requestCounter = new Counter('requests_total')

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 50 },    // Increase to 50 users
    { duration: '2m', target: 50 },    // Stay at 50 users
    { duration: '1m', target: 100 },   // Spike to 100 users
    { duration: '2m', target: 100 },   // Stay at 100 users
    { duration: '30s', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],                  // Error rate < 1%
    errors: ['rate<0.05'],                           // Custom error rate < 5%
    'http_req_duration{endpoint:couriers}': ['p(95)<400'],
    'http_req_duration{endpoint:vehicles}': ['p(95)<400'],
    'http_req_duration{endpoint:workflows}': ['p(95)<600'],
  },
}

// Base URL configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:3003'
const API_BASE = `${BASE_URL}/api`

// Test credentials
const ADMIN_CREDENTIALS = {
  email: 'admin@barq.com',
  password: 'admin123',
}

/**
 * Authenticate and get token
 */
function authenticate() {
  const loginRes = http.post(`${API_BASE}/auth/login`, JSON.stringify(ADMIN_CREDENTIALS), {
    headers: { 'Content-Type': 'application/json' },
    tags: { endpoint: 'auth' },
  })

  check(loginRes, {
    'login successful': (r) => r.status === 200,
    'token received': (r) => r.json('token') !== undefined,
  })

  return loginRes.json('token') || null
}

/**
 * Main test scenario
 */
export default function () {
  // Authenticate
  const token = authenticate()
  if (!token) {
    errorRate.add(1)
    return
  }

  const authHeaders = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  }

  // Test 1: Get Couriers
  group('Couriers API', () => {
    const couriersRes = http.get(`${API_BASE}/v1/couriers`, {
      headers: authHeaders,
      tags: { endpoint: 'couriers' },
    })

    const success = check(couriersRes, {
      'couriers status 200': (r) => r.status === 200,
      'couriers response time < 500ms': (r) => r.timings.duration < 500,
      'couriers has data': (r) => r.json('success') === true,
    })

    errorRate.add(!success)
    apiDuration.add(couriersRes.timings.duration, { endpoint: 'couriers' })
    requestCounter.add(1, { endpoint: 'couriers' })
  })

  sleep(1)

  // Test 2: Get Vehicles
  group('Vehicles API', () => {
    const vehiclesRes = http.get(`${API_BASE}/v1/vehicles`, {
      headers: authHeaders,
      tags: { endpoint: 'vehicles' },
    })

    const success = check(vehiclesRes, {
      'vehicles status 200': (r) => r.status === 200,
      'vehicles response time < 500ms': (r) => r.timings.duration < 500,
      'vehicles has data': (r) => r.json('success') === true,
    })

    errorRate.add(!success)
    apiDuration.add(vehiclesRes.timings.duration, { endpoint: 'vehicles' })
    requestCounter.add(1, { endpoint: 'vehicles' })
  })

  sleep(1)

  // Test 3: Get Workflows
  group('Workflows API', () => {
    const workflowsRes = http.get(`${API_BASE}/v1/workflows`, {
      headers: authHeaders,
      tags: { endpoint: 'workflows' },
    })

    const success = check(workflowsRes, {
      'workflows status 200': (r) => r.status === 200,
      'workflows response time < 600ms': (r) => r.timings.duration < 600,
      'workflows has data': (r) => r.json('success') === true,
    })

    errorRate.add(!success)
    apiDuration.add(workflowsRes.timings.duration, { endpoint: 'workflows' })
    requestCounter.add(1, { endpoint: 'workflows' })
  })

  sleep(1)

  // Test 4: Get Dashboard Stats
  group('Dashboard API', () => {
    const dashboardRes = http.get(`${API_BASE}/v1/dashboard/stats`, {
      headers: authHeaders,
      tags: { endpoint: 'dashboard' },
    })

    const success = check(dashboardRes, {
      'dashboard status 200': (r) => r.status === 200,
      'dashboard response time < 1000ms': (r) => r.timings.duration < 1000,
    })

    errorRate.add(!success)
    apiDuration.add(dashboardRes.timings.duration, { endpoint: 'dashboard' })
    requestCounter.add(1, { endpoint: 'dashboard' })
  })

  sleep(1)

  // Test 5: Search Operation
  group('Search API', () => {
    const searchRes = http.get(`${API_BASE}/v1/couriers?search=ahmed`, {
      headers: authHeaders,
      tags: { endpoint: 'search' },
    })

    const success = check(searchRes, {
      'search status 200': (r) => r.status === 200,
      'search response time < 300ms': (r) => r.timings.duration < 300,
    })

    errorRate.add(!success)
    apiDuration.add(searchRes.timings.duration, { endpoint: 'search' })
    requestCounter.add(1, { endpoint: 'search' })
  })

  sleep(2)
}

/**
 * Setup function - runs once before test
 */
export function setup() {
  console.log('Starting API load test...')
  console.log(`Base URL: ${BASE_URL}`)
  return { startTime: new Date() }
}

/**
 * Teardown function - runs once after test
 */
export function teardown(data) {
  const duration = (new Date() - data.startTime) / 1000
  console.log(`Test completed in ${duration} seconds`)
}

/**
 * Handle summary data
 */
export function handleSummary(data) {
  return {
    'load-test-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  }
}

function textSummary(data, options) {
  const indent = options?.indent || ''
  const enableColors = options?.enableColors || false

  let output = '\n'
  output += `${indent}================================================================================\n`
  output += `${indent}                           Load Test Summary                                  \n`
  output += `${indent}================================================================================\n\n`

  // Request stats
  output += `${indent}Total Requests: ${data.metrics.requests_total?.values?.count || 0}\n`
  output += `${indent}Failed Requests: ${data.metrics.http_req_failed?.values?.rate || 0}%\n`
  output += `${indent}Error Rate: ${data.metrics.errors?.values?.rate || 0}%\n\n`

  // Duration stats
  output += `${indent}Response Time (p95): ${data.metrics.http_req_duration?.values['p(95)']?.toFixed(2) || 0}ms\n`
  output += `${indent}Response Time (p99): ${data.metrics.http_req_duration?.values['p(99)']?.toFixed(2) || 0}ms\n`
  output += `${indent}Average Response Time: ${data.metrics.http_req_duration?.values?.avg?.toFixed(2) || 0}ms\n\n`

  // Virtual users
  output += `${indent}Peak VUs: ${data.metrics.vus_max?.values?.max || 0}\n`
  output += `${indent}Test Duration: ${data.state?.testRunDurationMs ? (data.state.testRunDurationMs / 1000).toFixed(2) : 0}s\n\n`

  output += `${indent}================================================================================\n`

  return output
}
