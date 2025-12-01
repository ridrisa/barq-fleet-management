export type UserRole =
  | 'super_admin'
  | 'admin'
  | 'hr_manager'
  | 'fleet_manager'
  | 'viewer'
  | 'user'

export interface User {
  id: number
  email: string
  full_name?: string | null
  role: UserRole
  roles?: UserRole[]
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string | null
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

export * from './fleet'
