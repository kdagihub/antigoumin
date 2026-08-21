export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone_number: string
  auth_provider: 'email' | 'google' | 'apple'
  subscription_end_date: string | null
  alliance_badge_enabled?: boolean
  is_status_searchable?: boolean
  email_verified?: boolean
  phone_verified?: boolean
  is_fully_verified?: boolean
  has_alliance_vip?: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterPayload {
  email: string
  password: string
  first_name?: string
  last_name?: string
  phone_number: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface GoogleAuthPayload {
  id_token: string
}
