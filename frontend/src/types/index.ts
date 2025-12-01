export interface User {
  id: number
  email: string
  full_name?: string
  role: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface HealthResponse {
  status: string
  version: string
  database: string
}
