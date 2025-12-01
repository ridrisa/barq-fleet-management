/**
 * K6 Load Test: Workflow Operations
 * Tests workflow creation, approval, and state management under load
 */

import http from 'k6/http'
import { check, sleep, group } from 'k6'
import { Rate, Trend } from 'k6/metrics'

const errorRate = new Rate('workflow_errors')
const workflowDuration = new Trend('workflow_duration')

export const options = {
  stages: [
    { duration: '1m', target: 30 },    // Ramp up
    { duration: '3m', target: 30 },    // Sustained load
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.02'],
    workflow_errors: ['rate<0.05'],
  },
}

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3003'
const API_BASE = `${BASE_URL}/api`

function authenticate() {
  const loginRes = http.post(`${API_BASE}/auth/login`, JSON.stringify({
    email: 'admin@barq.com',
    password: 'admin123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  })

  return loginRes.json('token') || null
}

export default function () {
  const token = authenticate()
  if (!token) {
    errorRate.add(1)
    return
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  }

  // Test workflow creation
  group('Create Workflow', () => {
    const workflowData = {
      type: 'leave',
      title: `Leave Request - ${Date.now()}`,
      data: {
        startDate: '2025-02-01',
        endDate: '2025-02-05',
        reason: 'Annual leave',
      },
    }

    const createRes = http.post(
      `${API_BASE}/v1/workflows`,
      JSON.stringify(workflowData),
      { headers }
    )

    const success = check(createRes, {
      'workflow created': (r) => r.status === 201 || r.status === 200,
      'workflow has ID': (r) => r.json('data.id') !== undefined,
    })

    errorRate.add(!success)
    workflowDuration.add(createRes.timings.duration)

    // Get workflow ID for subsequent operations
    const workflowId = createRes.json('data.id')

    if (workflowId) {
      sleep(1)

      // Test workflow approval
      group('Approve Workflow', () => {
        const approvalData = {
          action: 'approve',
          comments: 'Approved during load test',
        }

        const approveRes = http.post(
          `${API_BASE}/v1/workflows/${workflowId}/approve`,
          JSON.stringify(approvalData),
          { headers }
        )

        check(approveRes, {
          'approval successful': (r) => r.status === 200,
        })
      })
    }
  })

  sleep(2)

  // Test workflow listing
  group('List Workflows', () => {
    const listRes = http.get(`${API_BASE}/v1/workflows?page=1&limit=20`, { headers })

    check(listRes, {
      'list successful': (r) => r.status === 200,
      'list has data': (r) => r.json('data') !== undefined,
      'list response time ok': (r) => r.timings.duration < 600,
    })
  })

  sleep(1)
}
