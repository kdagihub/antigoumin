export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  auth_provider: 'email' | 'google' | 'apple'
  subscription_end_date: string | null
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
}

export interface LoginPayload {
  email: string
  password: string
}

export interface GoogleAuthPayload {
  id_token: string
}
