import axios from 'axios'

// API base URL - hardcoded for development, use env in production
const baseURL = 'http://localhost:8000/api/v1'

// Debug: log the baseURL in development
if (import.meta.env.DEV) {
  console.log('API baseURL:', baseURL)
}

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Helper to safely call APIs that may not exist yet
// Returns fallback on 404 errors (endpoint not implemented)
export const safeApiCall = async <T>(
  apiCall: () => Promise<T>,
  fallback: T
): Promise<T> => {
  try {
    return await apiCall()
  } catch (error: any) {
    if (error.response?.status === 404) {
      console.warn('API endpoint not implemented, using fallback')
      return fallback
    }
    throw error
  }
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor to handle 401 errors and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const { data } = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return data
  },
  getCurrentUser: async () => {
    const { data } = await api.get('/auth/me')
    return data
  },
  googleLogin: async (token: string) => {
    const { data } = await api.post('/auth/google', { token })
    return data
  },
}

export const healthAPI = {
  check: async () => {
    const { data } = await api.get('/health')
    return data
  },
}

export const dashboardAPI = {
  stats: async () => {
    const { data } = await api.get('/dashboard/stats')
    return data
  },
  getFinancialSummary: async () => {
    const { data } = await api.get('/dashboard/financial-summary')
    return data
  },
  getChartData: async (chartType: string, period?: string) => {
    const params = period ? `?period=${period}` : ''
    const { data } = await api.get(`/dashboard/charts/${chartType}${params}`)
    return data
  },
  getAlerts: async () => {
    const { data } = await api.get('/dashboard/alerts')
    return data
  },
  getTopCouriers: async (limit: number = 5) => {
    const { data } = await api.get(`/dashboard/performance/top-couriers?limit=${limit}`)
    return data
  },
  getRecentActivity: async (limit: number = 10) => {
    const { data } = await api.get(`/dashboard/recent-activity?limit=${limit}`)
    return data
  },
  getSummary: async () => {
    const { data } = await api.get('/dashboard/summary')
    return data
  },
  getMonthlyTrends: async () => {
    const { data } = await api.get('/dashboard/charts/monthly-trends')
    return data
  },
  getCourierStatus: async () => {
    const { data } = await api.get('/dashboard/charts/courier-status')
    return data
  },
  getSponsorshipDistribution: async () => {
    const { data } = await api.get('/dashboard/charts/sponsorship')
    return data
  },
  getProjectDistribution: async () => {
    const { data } = await api.get('/dashboard/charts/project-types')
    return data
  },
  getCityDistribution: async () => {
    const { data } = await api.get('/dashboard/charts/city-distribution')
    return data
  },
}

export const couriersAPI = {
  getAll: async (skip?: number, limit?: number) => {
    const params = new URLSearchParams()
    if (skip !== undefined) params.append('skip', skip.toString())
    // Default to high limit to fetch all couriers for filter options
    params.append('limit', (limit ?? 1000).toString())
    const { data } = await api.get(`/fleet/couriers?${params.toString()}`)
    return data
  },
  getById: async (id: number) => {
    const { data } = await api.get(`/fleet/couriers/${id}`)
    return data
  },
  getVehicleHistory: async (courierId: number) => {
    const { data } = await api.get(`/fleet/couriers/${courierId}/vehicle-history`)
    return data
  },
  getAssets: async (courierId: number) => {
    const { data } = await api.get(`/fleet/couriers/${courierId}/assets`)
    return data
  },
  getLoans: async (courierId: number) => {
    const { data } = await api.get(`/fleet/couriers/${courierId}/loans`)
    return data
  },
  create: async (courierData: any) => {
    const { data } = await api.post('/fleet/couriers', courierData)
    return data
  },
  update: async (id: number, courierData: any) => {
    const { data } = await api.put(`/fleet/couriers/${id}`, courierData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/fleet/couriers/${id}`)
    return data
  },
}

export const vehiclesAPI = {
  getAll: async () => {
    const { data } = await api.get('/fleet/vehicles')
    return data
  },
  create: async (vehicleData: any) => {
    const { data } = await api.post('/fleet/vehicles', vehicleData)
    return data
  },
  update: async (id: number, vehicleData: any) => {
    const { data } = await api.put(`/fleet/vehicles/${id}`, vehicleData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/fleet/vehicles/${id}`)
    return data
  },
}

export const assignmentsAPI = {
  getAll: async () => {
    const { data } = await api.get('/fleet/assignments')
    return data
  },
  create: async (assignmentData: any) => {
    const { data } = await api.post('/fleet/assignments', assignmentData)
    return data
  },
  update: async (id: number, assignmentData: any) => {
    const { data } = await api.put(`/fleet/assignments/${id}`, assignmentData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/fleet/assignments/${id}`)
    return data
  },
}

export const fuelTrackingAPI = {
  getAll: async () => {
    return safeApiCall(async () => {
      const { data } = await api.get('/fleet/fuel-logs')
      return data
    }, [])
  },
  create: async (fuelLogData: any) => {
    const { data } = await api.post('/fleet/fuel-logs', fuelLogData)
    return data
  },
  update: async (id: number, fuelLogData: any) => {
    const { data } = await api.put(`/fleet/fuel-logs/${id}`, fuelLogData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/fleet/fuel-logs/${id}`)
    return data
  },
  getSummary: async (startDate?: string, endDate?: string) => {
    return safeApiCall(async () => {
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      const { data } = await api.get(`/fleet/fuel-logs/summary?${params}`)
      return data
    }, { total_fuel: 0, total_cost: 0, average_efficiency: 0 })
  },
}

export const maintenanceAPI = {
  getAll: async () => {
    const { data } = await api.get('/fleet/maintenance')
    return data
  },
  create: async (maintenanceData: any) => {
    const { data } = await api.post('/fleet/maintenance', maintenanceData)
    return data
  },
  update: async (id: number, maintenanceData: any) => {
    const { data } = await api.put(`/fleet/maintenance/${id}`, maintenanceData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/fleet/maintenance/${id}`)
    return data
  },
  getUpcoming: async (days: number) => {
    const { data } = await api.get(`/fleet/maintenance/upcoming?days=${days}`)
    return data
  },
}

export const courierPerformanceAPI = {
  getAll: async (skip: number, limit: number, startDate: string, endDate: string) => {
    return safeApiCall(async () => {
      const { data } = await api.get(`/fleet/courier-performance?skip=${skip}&limit=${limit}&start_date=${startDate}&end_date=${endDate}`)
      return data
    }, { items: [], total: 0 })
  },
  exportToExcel: async (startDate: string, endDate: string) => {
    const { data } = await api.get(`/fleet/courier-performance/export?start_date=${startDate}&end_date=${endDate}`, {
      responseType: 'blob',
    })
    return data
  },
}

export const documentsAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/documents')
    return data
  },
  create: async (documentData: any) => {
    const { data } = await api.post('/operations/documents', documentData)
    return data
  },
  update: async (id: number, documentData: any) => {
    const { data } = await api.put(`/operations/documents/${id}`, documentData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/documents/${id}`)
    return data
  },
}

export const vehicleHistoryAPI = {
  getHistory: async (vehicleId: number) => {
    const { data } = await api.get(`/fleet/vehicles/${vehicleId}/history`)
    return data
  },
}

export const leavesAPI = {
  getAll: async () => {
    const { data } = await api.get('/hr/leave')
    return data
  },
  create: async (leaveData: any) => {
    const { data } = await api.post('/hr/leave', leaveData)
    return data
  },
  update: async (id: number, leaveData: any) => {
    const { data } = await api.put(`/hr/leave/${id}`, leaveData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/hr/leave/${id}`)
    return data
  },
}

export const loansAPI = {
  getAll: async () => {
    const { data } = await api.get('/hr/loan')
    return data
  },
  create: async (loanData: any) => {
    const { data } = await api.post('/hr/loan', loanData)
    return data
  },
  update: async (id: number, loanData: any) => {
    const { data } = await api.put(`/hr/loan/${id}`, loanData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/hr/loan/${id}`)
    return data
  },
}

export const attendanceAPI = {
  getAll: async () => {
    const { data } = await api.get('/hr/attendance')
    return data
  },
  create: async (attendanceData: any) => {
    const { data } = await api.post('/hr/attendance', attendanceData)
    return data
  },
  update: async (id: number, attendanceData: any) => {
    const { data } = await api.put(`/hr/attendance/${id}`, attendanceData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/hr/attendance/${id}`)
    return data
  },
}

export const salaryAPI = {
  getAll: async () => {
    const { data } = await api.get('/hr/salary')
    return data
  },
  calculate: async (salaryData: any) => {
    const { data } = await api.post('/hr/salary/calculate', salaryData)
    return data
  },
  save: async (salaryData: any) => {
    const { data } = await api.post('/hr/salary', salaryData)
    return data
  },
  getHistory: async (courierId: number) => {
    const { data } = await api.get(`/hr/salary/history/${courierId}`)
    return data
  },
  getByCourier: async (courierId: number) => {
    const { data } = await api.get(`/hr/salary?courier_id=${courierId}`)
    return data
  },
}

export const vehicleLogsAPI = {
  getAll: async () => {
    const { data } = await api.get('/fleet/vehicle-logs')
    return data
  },
  getByCourier: async (courierId: number) => {
    const { data } = await api.get(`/fleet/vehicle-logs?courier_id=${courierId}`)
    return data
  },
  getByVehicle: async (vehicleId: number) => {
    const { data } = await api.get(`/fleet/vehicle-logs?vehicle_id=${vehicleId}`)
    return data
  },
  create: async (logData: any) => {
    const { data } = await api.post('/fleet/vehicle-logs', logData)
    return data
  },
}

export const penaltiesAPI = {
  getAll: async () => {
    return safeApiCall(async () => {
      const { data } = await api.get('/hr/penalties')
      return data
    }, [])
  },
  create: async (penaltyData: any) => {
    const { data } = await api.post('/hr/penalties', penaltyData)
    return data
  },
  update: async (id: number, penaltyData: any) => {
    const { data } = await api.put(`/hr/penalties/${id}`, penaltyData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/hr/penalties/${id}`)
    return data
  },
}

export const assetsAPI = {
  getAll: async () => {
    const { data } = await api.get('/hr/asset')
    return data
  },
  getByCourier: async (courierId: number) => {
    const { data } = await api.get(`/hr/asset?courier_id=${courierId}`)
    return data
  },
  create: async (assetData: any) => {
    const { data } = await api.post('/hr/asset', assetData)
    return data
  },
  update: async (id: number, assetData: any) => {
    const { data } = await api.put(`/hr/asset/${id}`, assetData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/hr/asset/${id}`)
    return data
  },
}

export const payrollAPI = {
  generate: async (month: string) => {
    const { data } = await api.post('/hr/payroll/generate', { month })
    return data
  },
  approveAll: async (month: string) => {
    const { data } = await api.post('/hr/payroll/approve-all', { month })
    return data
  },
  process: async (month: string) => {
    const { data } = await api.post('/hr/payroll/process', { month })
    return data
  },
  export: async (month: string) => {
    const { data } = await api.get(`/hr/payroll/export?month=${month}`, {
      responseType: 'blob',
    })
    return data
  },
}

export const bonusesAPI = {
  getAll: async () => {
    return safeApiCall(async () => {
      const { data } = await api.get('/hr/bonuses')
      return data
    }, [])
  },
  create: async (bonusData: any) => {
    const { data } = await api.post('/hr/bonuses', bonusData)
    return data
  },
  update: async (id: number, bonusData: any) => {
    const { data } = await api.put(`/hr/bonuses/${id}`, bonusData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/hr/bonuses/${id}`)
    return data
  },
}

export const gosiAPI = {
  export: async (month: string) => {
    const { data } = await api.get(`/hr/gosi/export?month=${month}`, {
      responseType: 'blob',
    })
    return data
  },
}

export const eosAPI = {
  export: async (courierId: number) => {
    const { data } = await api.get(`/hr/eos/export/${courierId}`, {
      responseType: 'blob',
    })
    return data
  },
}

export const financialReportsAPI = {
  generate: async (reportType: string, startDate: string, endDate: string) => {
    const { data } = await api.get(`/finance/reports/${reportType}?start_date=${startDate}&end_date=${endDate}`)
    return data
  },
  export: async (reportId: number, format: 'excel' | 'pdf') => {
    const { data } = await api.get(`/finance/reports/export/${reportId}?format=${format}`, {
      responseType: 'blob',
    })
    return data
  },
}

export const expensesAPI = {
  getAll: async () => {
    const { data } = await api.get('/finance/expenses')
    return data
  },
  create: async (expenseData: any) => {
    const { data } = await api.post('/finance/expenses', expenseData)
    return data
  },
  update: async (id: number, expenseData: any) => {
    const { data } = await api.put(`/finance/expenses/${id}`, expenseData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/finance/expenses/${id}`)
    return data
  },
}

export const budgetsAPI = {
  getAll: async () => {
    const { data } = await api.get('/finance/budgets')
    return data
  },
  create: async (budgetData: any) => {
    const { data } = await api.post('/finance/budgets', budgetData)
    return data
  },
  update: async (id: number, budgetData: any) => {
    const { data } = await api.put(`/finance/budgets/${id}`, budgetData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/finance/budgets/${id}`)
    return data
  },
}

export const taxAPI = {
  generate: async (year: string) => {
    const { data} = await api.get(`/finance/tax/report?year=${year}`)
    return data
  },
  export: async (year: string, format: 'excel' | 'pdf') => {
    const { data } = await api.get(`/finance/tax/export?year=${year}&format=${format}`, {
      responseType: 'blob',
    })
    return data
  },
  downloadCertificate: async (year: string) => {
    const { data } = await api.get(`/finance/tax/certificate?year=${year}`, {
      responseType: 'blob',
    })
    return data
  },
}

// Operations Module APIs
export const codAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/cod')
    return data
  },
  create: async (codData: any) => {
    const { data } = await api.post('/operations/cod', codData)
    return data
  },
  update: async (id: number, codData: any) => {
    const { data } = await api.put(`/operations/cod/${id}`, codData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/cod/${id}`)
    return data
  },
  reconcile: async (id: number) => {
    const { data } = await api.post(`/operations/cod/${id}/reconcile`)
    return data
  },
}

export const deliveriesAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/deliveries')
    return data
  },
  create: async (deliveryData: any) => {
    const { data } = await api.post('/operations/deliveries', deliveryData)
    return data
  },
  update: async (id: number, deliveryData: any) => {
    const { data } = await api.put(`/operations/deliveries/${id}`, deliveryData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/deliveries/${id}`)
    return data
  },
  track: async (id: number) => {
    const { data } = await api.get(`/operations/deliveries/${id}/track`)
    return data
  },
}

export const documentationAPI = {
  getAll: async (filters?: { category?: string }) => {
    const params = new URLSearchParams()
    if (filters?.category) params.append('category', filters.category)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/operations/documents${query}`)
    return data
  },
  create: async (docData: any) => {
    const { data } = await api.post('/operations/documents', docData)
    return data
  },
  update: async (id: number, docData: any) => {
    const { data } = await api.put(`/operations/documents/${id}`, docData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/documents/${id}`)
    return data
  },
  trackView: async (id: number) => {
    const { data } = await api.post(`/operations/documents/${id}/view`)
    return data
  },
}

export const handoversAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/handovers')
    return data
  },
  create: async (handoverData: any) => {
    const { data } = await api.post('/operations/handovers', handoverData)
    return data
  },
  update: async (id: number, handoverData: any) => {
    const { data } = await api.put(`/operations/handovers/${id}`, handoverData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/handovers/${id}`)
    return data
  },
}

export const incidentsAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/incidents')
    return data
  },
  create: async (incidentData: any) => {
    const { data } = await api.post('/operations/incidents', incidentData)
    return data
  },
  update: async (id: number, incidentData: any) => {
    const { data } = await api.put(`/operations/incidents/${id}`, incidentData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/incidents/${id}`)
    return data
  },
}

export const routesAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/routes')
    return data
  },
  create: async (routeData: any) => {
    const { data } = await api.post('/operations/routes', routeData)
    return data
  },
  update: async (id: number, routeData: any) => {
    const { data } = await api.put(`/operations/routes/${id}`, routeData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/routes/${id}`)
    return data
  },
  optimize: async (routeIds: number[]) => {
    const { data } = await api.post('/operations/routes/optimize', { route_ids: routeIds })
    return data
  },
}

export const priorityQueueAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/priority-queue')
    return data
  },
  update: async (id: number, priority: number) => {
    const { data } = await api.put(`/operations/priority-queue/${id}`, { priority })
    return data
  },
}

export const zonesAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/zones')
    return data
  },
  create: async (zoneData: any) => {
    const { data } = await api.post('/operations/zones', zoneData)
    return data
  },
  update: async (id: number, zoneData: any) => {
    const { data } = await api.put(`/operations/zones/${id}`, zoneData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/zones/${id}`)
    return data
  },
}

export const dispatchAPI = {
  getAll: async () => {
    const { data } = await api.get('/operations/dispatch')
    return data
  },
  assign: async (deliveryId: number, courierId: number) => {
    const { data } = await api.post('/operations/dispatch/assign', { delivery_id: deliveryId, courier_id: courierId })
    return data
  },
  reassign: async (deliveryId: number, courierId: number) => {
    const { data } = await api.post('/operations/dispatch/reassign', { delivery_id: deliveryId, courier_id: courierId })
    return data
  },
  updateStatus: async (deliveryId: number, status: string) => {
    const { data } = await api.patch(`/operations/dispatch/${deliveryId}/status`, { status })
    return data
  },
}

export const feedbackAPI = {
  getAll: async (skip?: number, limit?: number) => {
    const params = new URLSearchParams()
    if (skip !== undefined) params.append('skip', skip.toString())
    if (limit !== undefined) params.append('limit', limit.toString())
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/operations/feedback${query}`)
    return data
  },
  create: async (feedbackData: any) => {
    const { data } = await api.post('/operations/feedback', feedbackData)
    return data
  },
  getRatingSummary: async () => {
    const { data } = await api.get('/operations/feedback/summary')
    return data
  },
  addResponse: async (id: number, response: string) => {
    const { data } = await api.post(`/operations/feedback/${id}/response`, { response })
    return data
  },
}

export const performanceAPI = {
  getCourierPerformance: async (courierId?: number) => {
    // Backend uses /fleet/courier-performance for courier metrics
    const url = courierId ? `/fleet/courier-performance?courier_id=${courierId}` : '/fleet/courier-performance'
    const { data } = await api.get(url)
    return data
  },
  getOperationsMetrics: async () => {
    // Backend has system performance at /performance/metrics and dispatch metrics at /operations/dispatch/metrics
    const { data } = await api.get('/operations/dispatch/metrics')
    return data
  },
  getSystemMetrics: async () => {
    const { data } = await api.get('/performance/metrics')
    return data
  },
}

export const operationsSettingsAPI = {
  get: async () => {
    const { data } = await api.get('/operations/settings')
    return data
  },
  getAll: async () => {
    const { data } = await api.get('/operations/settings')
    return data
  },
  update: async (settings: any) => {
    const { data } = await api.put('/operations/settings', settings)
    return data
  },
  reset: async () => {
    const { data } = await api.post('/operations/settings/reset')
    return data
  },
}

export const deliveryAssignmentsAPI = {
  getAll: async () => {
    // Backend uses /operations/dispatch for dispatch assignments
    const { data } = await api.get('/operations/dispatch')
    return data
  },
  assign: async (deliveryId: number, courierId: number) => {
    const { data } = await api.post('/operations/dispatch', { delivery_id: deliveryId, courier_id: courierId })
    return data
  },
  reassign: async (deliveryId: number, courierId: number) => {
    const { data } = await api.post(`/operations/dispatch/${deliveryId}/reassign`, { new_courier_id: courierId, reassignment_reason: 'Manual reassignment' })
    return data
  },
  updateStatus: async (deliveryId: number, status: string) => {
    const { data } = await api.patch(`/operations/deliveries/${deliveryId}/status`, { status })
    return data
  },
}

export const qualityControlAPI = {
  getAll: async () => {
    // Backend uses /operations/quality/inspections for quality inspections
    const { data } = await api.get('/operations/quality/inspections')
    return data
  },
  getMetrics: async () => {
    const { data } = await api.get('/operations/quality/metrics')
    return data
  },
  create: async (inspectionData: any) => {
    const { data } = await api.post('/operations/quality/inspections', inspectionData)
    return data
  },
  update: async (id: number, inspectionData: any) => {
    const { data } = await api.put(`/operations/quality/inspections/${id}`, inspectionData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/quality/inspections/${id}`)
    return data
  },
  complete: async (id: number, completionData: any) => {
    const { data } = await api.post(`/operations/quality/inspections/${id}/complete`, completionData)
    return data
  },
}

export const serviceLevelsAPI = {
  getAll: async () => {
    // Backend uses /operations/sla/definitions for SLA definitions
    const { data } = await api.get('/operations/sla/definitions')
    return data
  },
  getTracking: async (status?: string) => {
    const params = status ? `?status=${status}` : ''
    const { data } = await api.get(`/operations/sla/tracking${params}`)
    return data
  },
  getAtRisk: async () => {
    const { data } = await api.get('/operations/sla/tracking/at-risk')
    return data
  },
  getBreached: async () => {
    const { data } = await api.get('/operations/sla/tracking/breached')
    return data
  },
  create: async (slaData: any) => {
    const { data } = await api.post('/operations/sla/definitions', slaData)
    return data
  },
  update: async (id: number, slaData: any) => {
    const { data } = await api.put(`/operations/sla/definitions/${id}`, slaData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/operations/sla/definitions/${id}`)
    return data
  },
  getComplianceReport: async (period?: string) => {
    const params = period ? `?period=${period}` : ''
    const { data } = await api.get(`/operations/sla/compliance/report${params}`)
    return data
  },
}

// Accommodation Module APIs
export const buildingsAPI = {
  getAll: async (skip?: number, limit?: number) => {
    const params = new URLSearchParams()
    if (skip !== undefined) params.append('skip', skip.toString())
    if (limit !== undefined) params.append('limit', limit.toString())
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/accommodation/buildings${query}`)
    return data
  },
  create: async (buildingData: any) => {
    const { data } = await api.post('/accommodation/buildings', buildingData)
    return data
  },
  update: async (id: number, buildingData: any) => {
    const { data } = await api.put(`/accommodation/buildings/${id}`, buildingData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/buildings/${id}`)
    return data
  },
}

export const roomsAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/rooms')
    return data
  },
  create: async (roomData: any) => {
    const { data } = await api.post('/accommodation/rooms', roomData)
    return data
  },
  update: async (id: number, roomData: any) => {
    const { data } = await api.put(`/accommodation/rooms/${id}`, roomData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/rooms/${id}`)
    return data
  },
}

export const bedsAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/beds')
    return data
  },
  create: async (bedData: any) => {
    const { data } = await api.post('/accommodation/beds', bedData)
    return data
  },
  update: async (id: number, bedData: any) => {
    const { data } = await api.put(`/accommodation/beds/${id}`, bedData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/beds/${id}`)
    return data
  },
}

export const bedAssignmentsAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/bed-assignments')
    return data
  },
  create: async (assignmentData: any) => {
    const { data } = await api.post('/accommodation/bed-assignments', assignmentData)
    return data
  },
  update: async (id: number, assignmentData: any) => {
    const { data } = await api.put(`/accommodation/bed-assignments/${id}`, assignmentData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/bed-assignments/${id}`)
    return data
  },
}

export const allocationsAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/allocations')
    return data
  },
  getByCourier: async (courierId: number) => {
    const { data } = await api.get(`/accommodation/allocations/courier/${courierId}`)
    return data
  },
  create: async (allocationData: any) => {
    const { data } = await api.post('/accommodation/allocations', allocationData)
    return data
  },
  update: async (id: number, allocationData: any) => {
    const { data } = await api.put(`/accommodation/allocations/${id}`, allocationData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/allocations/${id}`)
    return data
  },
}

export const accommodationMaintenanceAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/maintenance')
    return data
  },
  create: async (maintenanceData: any) => {
    const { data } = await api.post('/accommodation/maintenance', maintenanceData)
    return data
  },
  update: async (id: number, maintenanceData: any) => {
    const { data } = await api.put(`/accommodation/maintenance/${id}`, maintenanceData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/maintenance/${id}`)
    return data
  },
}

export const utilitiesAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/utilities')
    return data
  },
  create: async (utilityData: any) => {
    const { data } = await api.post('/accommodation/utilities', utilityData)
    return data
  },
  update: async (id: number, utilityData: any) => {
    const { data } = await api.put(`/accommodation/utilities/${id}`, utilityData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/utilities/${id}`)
    return data
  },
}

export const accommodationInventoryAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/inventory')
    return data
  },
  create: async (inventoryData: any) => {
    const { data } = await api.post('/accommodation/inventory', inventoryData)
    return data
  },
  update: async (id: number, inventoryData: any) => {
    const { data } = await api.put(`/accommodation/inventory/${id}`, inventoryData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/inventory/${id}`)
    return data
  },
}

export const contractsAPI = {
  getAll: async () => {
    const { data } = await api.get('/accommodation/contracts')
    return data
  },
  create: async (contractData: any) => {
    const { data } = await api.post('/accommodation/contracts', contractData)
    return data
  },
  update: async (id: number, contractData: any) => {
    const { data } = await api.put(`/accommodation/contracts/${id}`, contractData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/accommodation/contracts/${id}`)
    return data
  },
  uploadDocument: async (id: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post(`/accommodation/contracts/${id}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },
}

// Workflows Module APIs
export const workflowTemplatesAPI = {
  getAll: async () => {
    const { data } = await api.get('/workflow/template')
    return data
  },
  create: async (templateData: any) => {
    const { data } = await api.post('/workflow/template', templateData)
    return data
  },
  update: async (id: number, templateData: any) => {
    const { data } = await api.put(`/workflow/template/${id}`, templateData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/workflow/template/${id}`)
    return data
  },
  activate: async (id: number) => {
    const { data } = await api.post(`/workflow/template/${id}/activate`)
    return data
  },
  deactivate: async (id: number) => {
    const { data } = await api.post(`/workflow/template/${id}/deactivate`)
    return data
  },
}

export const workflowInstancesAPI = {
  getAll: async () => {
    const { data } = await api.get('/workflow/instance')
    return data
  },
  create: async (instanceData: any) => {
    const { data } = await api.post('/workflow/instance', instanceData)
    return data
  },
  get: async (id: number) => {
    const { data } = await api.get(`/workflow/instance/${id}`)
    return data
  },
  update: async (id: number, instanceData: any) => {
    const { data } = await api.put(`/workflow/instance/${id}`, instanceData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/workflow/instance/${id}`)
    return data
  },
  approve: async (id: number) => {
    const { data } = await api.post(`/workflow/instance/${id}/approve`)
    return data
  },
  reject: async (id: number, reason: string) => {
    const { data } = await api.post(`/workflow/instance/${id}/reject`, { reason })
    return data
  },
}

export const approvalChainsAPI = {
  getAll: async () => {
    const { data } = await api.get('/workflow/approval-chains')
    return data
  },
  create: async (chainData: any) => {
    const { data } = await api.post('/workflow/approval-chains', chainData)
    return data
  },
  update: async (id: number, chainData: any) => {
    const { data } = await api.put(`/workflow/approval-chains/${id}`, chainData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/workflow/approval-chains/${id}`)
    return data
  },
}

// Support Module APIs
export const ticketsAPI = {
  getAll: async (skip?: number, limit?: number, filters?: { status?: string; priority?: string }) => {
    const params = new URLSearchParams()
    if (skip !== undefined) params.append('skip', skip.toString())
    if (limit !== undefined) params.append('limit', limit.toString())
    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/support/tickets${query}`)
    return data
  },
  getById: async (id: number) => {
    const { data } = await api.get(`/support/tickets/${id}`)
    return data
  },
  create: async (ticketData: any) => {
    const { data } = await api.post('/support/tickets', ticketData)
    return data
  },
  update: async (id: number, ticketData: any) => {
    const { data } = await api.put(`/support/tickets/${id}`, ticketData)
    return data
  },
  updateStatus: async (id: number, status: string) => {
    const { data } = await api.patch(`/support/tickets/${id}/status`, { status })
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/support/tickets/${id}`)
    return data
  },
  reply: async (id: number, message: string) => {
    const { data } = await api.post(`/support/tickets/${id}/reply`, { message })
    return data
  },
  addComment: async (id: number, comment: string) => {
    const { data } = await api.post(`/support/tickets/${id}/comments`, { content: comment })
    return data
  },
}

export const knowledgeBaseAPI = {
  getAll: async (filters?: { category?: string }) => {
    const params = new URLSearchParams()
    if (filters?.category) params.append('category', filters.category)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/support/kb${query}`)
    return data
  },
  create: async (articleData: any) => {
    const { data } = await api.post('/support/kb', articleData)
    return data
  },
  update: async (id: number, articleData: any) => {
    const { data } = await api.put(`/support/kb/${id}`, articleData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/support/kb/${id}`)
    return data
  },
  getTags: async () => {
    const { data } = await api.get('/support/kb/tags')
    return data
  },
}

export const faqAPI = {
  getAll: async (filters?: { category?: string }) => {
    const params = new URLSearchParams()
    if (filters?.category) params.append('category', filters.category)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/support/faq${query}`)
    return data
  },
  create: async (faqData: any) => {
    const { data } = await api.post('/support/faq', faqData)
    return data
  },
  update: async (id: number, faqData: any) => {
    const { data } = await api.put(`/support/faq/${id}`, faqData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/support/faq/${id}`)
    return data
  },
  markHelpful: async (id: number) => {
    const { data } = await api.post(`/support/faq/${id}/helpful`)
    return data
  },
}

export const contactSupportAPI = {
  send: async (message: any) => {
    const { data } = await api.post('/support/contact', message)
    return data
  },
  submit: async (formData: any) => {
    const { data } = await api.post('/support/contact', formData)
    return data
  },
}

export const supportAnalyticsAPI = {
  // Use the comprehensive dashboard endpoint that returns all metrics
  getDashboard: async (days: number = 30) => {
    return safeApiCall(async () => {
      const { data } = await api.get(`/support/analytics/dashboard?days=${days}`)
      return data
    }, {
      period: { start_date: '', end_date: '', days },
      tickets: { total_tickets: 0, open_tickets: 0, closed_tickets: 0, resolved_tickets: 0 },
      response_times: { avg_first_response_hours: 0, avg_resolution_hours: 0 },
      sla: { sla_compliance_rate: 0 },
      customer_satisfaction: { satisfaction_score: 0, response_count: 0 },
    })
  },
  // Get ticket metrics
  getTickets: async (startDate?: string, endDate?: string) => {
    return safeApiCall(async () => {
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      const query = params.toString() ? `?${params}` : ''
      const { data } = await api.get(`/support/analytics/tickets${query}`)
      return data
    }, { total_tickets: 0, open_tickets: 0, closed_tickets: 0, resolved_tickets: 0 })
  },
  // Get response time metrics
  getResponseTimes: async (startDate?: string, endDate?: string) => {
    return safeApiCall(async () => {
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      const query = params.toString() ? `?${params}` : ''
      const { data } = await api.get(`/support/analytics/response-times${query}`)
      return data
    }, { avg_first_response_hours: 0, avg_resolution_hours: 0 })
  },
  // Get customer satisfaction
  getCustomerSatisfaction: async (startDate?: string, endDate?: string) => {
    return safeApiCall(async () => {
      const params = new URLSearchParams()
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      const query = params.toString() ? `?${params}` : ''
      const { data } = await api.get(`/support/analytics/customer-satisfaction${query}`)
      return data
    }, { satisfaction_score: 0, response_count: 0 })
  },
  // Get trend data (requires start_date and end_date)
  getTrends: async (startDate: string, endDate: string) => {
    return safeApiCall(async () => {
      const { data } = await api.get(`/support/analytics/trends?start_date=${startDate}&end_date=${endDate}`)
      return data
    }, [])
  },
  // Legacy compatibility methods for SupportAnalytics page
  getSummary: async (_startDate: string, _endDate: string) => {
    return safeApiCall(async () => {
      const { data } = await api.get('/support/analytics/dashboard?days=30')
      return {
        totalTickets: data.tickets?.total_tickets || 0,
        openTickets: data.tickets?.open_tickets || 0,
        avgResolutionTime: data.response_times?.avg_resolution_hours || 0,
        customerSatisfaction: data.customer_satisfaction?.satisfaction_score || 0,
      }
    }, { totalTickets: 0, openTickets: 0, avgResolutionTime: 0, customerSatisfaction: 0 })
  },
  getTicketsOverTime: async (startDate: string, endDate: string) => {
    return safeApiCall(async () => {
      const { data } = await api.get(`/support/analytics/trends?start_date=${startDate}&end_date=${endDate}`)
      return Array.isArray(data) ? data : []
    }, [])
  },
  // These endpoints don't exist - return empty arrays
  getTicketsByCategory: async (_startDate?: string, _endDate?: string) => [],
  getResolutionTimeByCategory: async (_startDate?: string, _endDate?: string) => [],
  getCommonIssues: async (_startDate?: string, _endDate?: string) => [],
}

// Admin Module APIs
export const usersAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/users')
    return data
  },
  create: async (userData: any) => {
    const { data } = await api.post('/admin/users', userData)
    return data
  },
  update: async (id: number, userData: any) => {
    const { data } = await api.put(`/admin/users/${id}`, userData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/admin/users/${id}`)
    return data
  },
}

export const adminUsersAPI = usersAPI

export const rolesAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/roles')
    return data
  },
  create: async (roleData: any) => {
    const { data } = await api.post('/admin/roles', roleData)
    return data
  },
  update: async (id: number, roleData: any) => {
    const { data } = await api.put(`/admin/roles/${id}`, roleData)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/admin/roles/${id}`)
    return data
  },
}

export const permissionsAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/permissions')
    return data
  },
  update: async (roleId: number, permissions: any) => {
    const { data } = await api.put(`/admin/permissions/${roleId}`, { permissions })
    return data
  },
}

export const auditLogsAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/audit-logs')
    return data
  },
  export: async (startDate: string, endDate: string) => {
    const { data } = await api.get(`/admin/audit-logs/export?start_date=${startDate}&end_date=${endDate}`, {
      responseType: 'blob',
    })
    return data
  },
}

export const backupsAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/backups')
    return data
  },
  create: async () => {
    const { data } = await api.post('/admin/backups')
    return data
  },
  restore: async (id: number) => {
    const { data } = await api.post(`/admin/backups/${id}/restore`)
    return data
  },
  delete: async (id: number) => {
    const { data } = await api.delete(`/admin/backups/${id}`)
    return data
  },
}

export const apiKeysAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/api-keys')
    return data
  },
  create: async (keyData: any) => {
    const { data } = await api.post('/admin/api-keys', keyData)
    return data
  },
  revoke: async (id: number) => {
    const { data } = await api.delete(`/admin/api-keys/${id}`)
    return data
  },
}

export const adminAPI = {
  getSystemMonitoring: async () => {
    // Use the working resources endpoint instead of non-existent /monitoring
    return safeApiCall(async () => {
      const { data } = await api.get('/admin/monitoring/resources')
      return data
    }, {
      cpu_count: 0,
      cpu_usage_percent: 0,
      memory_usage_percent: 0,
      disk_usage_percent: 0,
    })
  },
  getIntegrations: async () => {
    return safeApiCall(async () => {
      const { data } = await api.get('/admin/integrations')
      return data
    }, [])
  },
}

export const emailTemplatesAPI = {
  getAll: async () => {
    const { data } = await api.get('/admin/email-templates')
    return data
  },
  update: async (id: number, templateData: any) => {
    const { data } = await api.put(`/admin/email-templates/${id}`, templateData)
    return data
  },
}

// Settings Module APIs
export const settingsAPI = {
  get: async () => {
    const { data } = await api.get('/settings/system')
    return data
  },
  update: async (settings: any) => {
    const { data } = await api.put('/settings/system', settings)
    return data
  },
  getGeneral: async () => {
    const { data } = await api.get('/settings/general')
    return data
  },
  updateGeneral: async (settings: any) => {
    const { data } = await api.put('/settings/general', settings)
    return data
  },
  getNotifications: async () => {
    const { data } = await api.get('/settings/notifications')
    return data
  },
  updateNotifications: async (settings: any) => {
    const { data } = await api.put('/settings/notifications', settings)
    return data
  },
}

export const profileAPI = {
  get: async () => {
    const { data } = await api.get('/settings/user/profile')
    return data
  },
  update: async (profileData: any) => {
    const { data } = await api.put('/settings/user/profile', profileData)
    return data
  },
  uploadPhoto: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/settings/user/profile/photo', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },
  changePassword: async (passwordData: { current_password: string; new_password: string }) => {
    const { data } = await api.put('/settings/user/password', passwordData)
    return data
  },
  getNotificationPreferences: async () => {
    const { data } = await api.get('/settings/user/notifications')
    return data
  },
  updateNotificationPreferences: async (preferences: any) => {
    const { data } = await api.put('/settings/user/notifications', preferences)
    return data
  },
}

export const preferencesAPI = {
  get: async () => {
    const { data } = await api.get('/settings/user/preferences')
    return data
  },
  update: async (preferences: any) => {
    const { data } = await api.put('/settings/user/preferences', preferences)
    return data
  },
  reset: async () => {
    const { data } = await api.post('/settings/user/preferences/reset')
    return data
  },
}

export const notificationSettingsAPI = {
  get: async () => {
    const { data } = await api.get('/settings/notifications')
    return data
  },
  update: async (settings: any) => {
    const { data } = await api.put('/settings/notifications', settings)
    return data
  },
}

export const generalSettingsAPI = {
  get: async () => {
    const { data } = await api.get('/settings/general')
    return data
  },
  update: async (settings: any) => {
    const { data } = await api.put('/settings/general', settings)
    return data
  },
}

// FMS (Fleet Management System) API - Integration with machinettalk via backend proxy
// All FMS requests go through our backend to keep API keys secure
export const fmsAPI = {
  // Get all tracked assets/vehicles from FMS
  getAssets: async (pageSize?: number, pageIndex?: number) => {
    const params = new URLSearchParams()
    if (pageSize) params.append('page_size', pageSize.toString())
    if (pageIndex) params.append('page_index', pageIndex.toString())
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/fms/assets${query}`)
    return data
  },
  // Get single asset by ID
  getAssetById: async (assetId: number) => {
    const { data } = await api.get(`/fms/assets/${assetId}`)
    return data
  },
  // Get asset by plate number
  getAssetByPlate: async (plateNumber: string) => {
    const { data } = await api.get(`/fms/assets/plate/${plateNumber}`)
    return data
  },
  // Get location history for an asset
  getLocationHistory: async (assetId: number, from: string, to: string) => {
    const { data } = await api.get(`/fms/assets/${assetId}/history?from_time=${from}&to_time=${to}`)
    return data
  },
  // Search nearby assets
  searchNearby: async (latitude: number, longitude: number, radiusKm?: number) => {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
    })
    if (radiusKm) params.append('radius_km', radiusKm.toString())
    const { data } = await api.get(`/fms/assets/search/nearby?${params}`)
    return data
  },
  // Get all geofences
  getGeofences: async (pageSize?: number, pageIndex?: number) => {
    const params = new URLSearchParams()
    if (pageSize) params.append('page_size', pageSize.toString())
    if (pageIndex) params.append('page_index', pageIndex.toString())
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/fms/geofences${query}`)
    return data
  },
  // Get geofence by ID
  getGeofenceById: async (zoneId: number) => {
    const { data } = await api.get(`/fms/geofences/${zoneId}`)
    return data
  },
  // Get all placemarks
  getPlacemarks: async (pageSize?: number, pageIndex?: number) => {
    const params = new URLSearchParams()
    if (pageSize) params.append('page_size', pageSize.toString())
    if (pageIndex) params.append('page_index', pageIndex.toString())
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/fms/placemarks${query}`)
    return data
  },
  // Create placemark
  createPlacemark: async (placemark: {
    PlacemarkName: string
    PlacemarkNameAr: string
    Latitude: number
    Longitude: number
    Color?: string
  }) => {
    const { data } = await api.post('/fms/placemarks', placemark)
    return data
  },
  // Update placemark
  updatePlacemark: async (id: number, placemark: Partial<{
    PlacemarkName: string
    PlacemarkNameAr: string
    Latitude: number
    Longitude: number
    Color?: string
  }>) => {
    const { data } = await api.put(`/fms/placemarks/${id}`, placemark)
    return data
  },
  // Delete placemark
  deletePlacemark: async (id: number) => {
    const { data } = await api.delete(`/fms/placemarks/${id}`)
    return data
  },
  // Get FMS connection status
  getStatus: async () => {
    const { data } = await api.get('/fms/tracking/status')
    return data
  },
  // Get FMS health
  getHealth: async () => {
    const { data } = await api.get('/fms/tracking/health')
    return data
  },
  // Get fleet summary (active, idle, offline counts)
  getFleetSummary: async () => {
    const { data } = await api.get('/fms/tracking/summary')
    return data
  },
  // Get current position for a vehicle
  getVehicleCurrentPosition: async (vehicleId: number) => {
    const { data } = await api.get(`/fms/tracking/vehicles/${vehicleId}/current`)
    return data
  },
  // Get SSE stream URL info
  getStreamInfo: async () => {
    const { data } = await api.get('/fms/tracking/stream-url')
    return data
  },
}

// FMS Sync API - Sync FMS data with BARQ couriers/vehicles
export const fmsSyncAPI = {
  // Get all live courier locations from FMS
  getLiveLocations: async () => {
    const { data } = await api.get('/fms/sync/live-locations')
    return data
  },
  // Get live location for a specific courier by ID
  getCourierLocation: async (courierId: number) => {
    const { data } = await api.get(`/fms/sync/courier/${courierId}/location`)
    return data
  },
  // Get sync statistics
  getStats: async () => {
    const { data } = await api.get('/fms/sync/stats')
    return data
  },
  // Preview sync matches
  previewSync: async () => {
    const { data } = await api.get('/fms/sync/preview')
    return data
  },
  // Run FMS sync
  runSync: async () => {
    const { data } = await api.post('/fms/sync/run')
    return data
  },
}

// Organization/Tenant Module APIs
export const organizationAPI = {
  // Get all organizations user belongs to
  getAll: async () => {
    const { data } = await api.get('/auth/me/organizations')
    return data
  },
  // Get current organization details
  getCurrent: async () => {
    const { data } = await api.get('/tenant/organizations/current')
    return data
  },
  // Get organization by ID
  getById: async (id: number) => {
    const { data } = await api.get(`/tenant/organizations/${id}`)
    return data
  },
  // Create organization
  create: async (orgData: { name: string; slug?: string }) => {
    const { data } = await api.post('/tenant/organizations', orgData)
    return data
  },
  // Update organization
  update: async (id: number, orgData: any) => {
    const { data } = await api.put(`/tenant/organizations/${id}`, orgData)
    return data
  },
  // Delete organization
  delete: async (id: number) => {
    const { data } = await api.delete(`/tenant/organizations/${id}`)
    return data
  },
  // Get organization statistics
  getStatistics: async (id: number) => {
    const { data } = await api.get(`/tenant/organizations/${id}/statistics`)
    return data
  },
  // Upgrade subscription
  upgrade: async (id: number, planData: { subscription_plan: string; max_users?: number; max_couriers?: number; max_vehicles?: number }) => {
    const { data } = await api.post(`/tenant/organizations/${id}/upgrade`, planData)
    return data
  },
  // Switch organization (get new token)
  switch: async (organizationId: number) => {
    const { data } = await api.post('/auth/switch-organization', { organization_id: organizationId })
    return data
  },
  // Organization members
  members: {
    getAll: async (organizationId: number) => {
      const { data } = await api.get(`/tenant/organizations/${organizationId}/members`)
      return data
    },
    add: async (organizationId: number, memberData: { user_id: number; role: string }) => {
      const { data } = await api.post(`/tenant/organizations/${organizationId}/members`, memberData)
      return data
    },
    update: async (organizationId: number, userId: number, memberData: { role?: string; is_active?: boolean }) => {
      const { data } = await api.put(`/tenant/organizations/${organizationId}/members/${userId}`, memberData)
      return data
    },
    remove: async (organizationId: number, userId: number) => {
      const { data } = await api.delete(`/tenant/organizations/${organizationId}/members/${userId}`)
      return data
    },
    leave: async (organizationId: number) => {
      const { data } = await api.post(`/tenant/organizations/${organizationId}/leave`)
      return data
    },
  },
  // Convenience aliases for OrganizationSettings page
  get: async (id: number) => {
    const { data } = await api.get(`/tenant/organizations/${id}`)
    return data
  },
  getMembers: async (organizationId: number) => {
    const { data } = await api.get(`/tenant/organizations/${organizationId}/members`)
    return data
  },
  inviteMember: async (organizationId: number, memberData: { email: string; role: string }) => {
    const { data } = await api.post(`/tenant/organizations/${organizationId}/invite`, memberData)
    return data
  },
  removeMember: async (organizationId: number, userId: number) => {
    const { data } = await api.delete(`/tenant/organizations/${organizationId}/members/${userId}`)
    return data
  },
  updateMemberRole: async (organizationId: number, userId: number, role: string) => {
    const { data } = await api.put(`/tenant/organizations/${organizationId}/members/${userId}`, { role })
    return data
  },
}

// Analytics Module APIs
export const analyticsAPI = {
  // Overview Dashboard
  getDashboard: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/overview/dashboard${query}`)
    return data
  },

  // KPI Dashboard
  getKPIDashboard: async (period?: string) => {
    const params = period ? `?period=${period}` : ''
    const { data } = await api.get(`/analytics/kpi/dashboard${params}`)
    return data
  },

  // Fleet Analytics
  getFleetUtilization: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/fleet/utilization${query}`)
    return data
  },
  getFleetPerformance: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/fleet/performance${query}`)
    return data
  },

  // HR Analytics
  getHRAttendance: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/hr/attendance${query}`)
    return data
  },
  getHRLeave: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/hr/leave${query}`)
    return data
  },

  // Financial Analytics
  getFinancialRevenue: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/financial/revenue${query}`)
    return data
  },
  getFinancialExpenses: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/financial/expenses${query}`)
    return data
  },

  // Operations Analytics
  getOperationsDeliveries: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/operations/deliveries${query}`)
    return data
  },
  getOperationsPerformance: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const query = params.toString() ? `?${params}` : ''
    const { data } = await api.get(`/analytics/operations/performance${query}`)
    return data
  },

  // Export Reports
  exportReport: async (reportType: string, format: 'excel' | 'pdf', startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ format })
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const { data } = await api.get(`/analytics/reports/${reportType}/export?${params}`, {
      responseType: 'blob',
    })
    return data
  },
}