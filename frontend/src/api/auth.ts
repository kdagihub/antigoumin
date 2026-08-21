import { apiRequest } from './client'
import type {
  GoogleAuthPayload,
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  User,
} from '@/types/user'

export function register(payload: RegisterPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/register', {
    method: 'POST',
    data: payload,
  })
}

export function login(payload: LoginPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    data: payload,
  })
}

export function loginWithGoogle(payload: GoogleAuthPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/google', {
    method: 'POST',
    data: payload,
  })
}

export function fetchMe(): Promise<User> {
  return apiRequest<User>('/me')
}

export function updateStatusVisibility(isStatusSearchable: boolean): Promise<User> {
  return apiRequest<User>('/auth/me/status-visibility', {
    method: 'PATCH',
    data: { is_status_searchable: isStatusSearchable },
  })
}
