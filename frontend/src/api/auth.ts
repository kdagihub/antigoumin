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
    body: payload,
  })
}

export function login(payload: LoginPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    body: payload,
  })
}

export function loginWithGoogle(payload: GoogleAuthPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/auth/google', {
    method: 'POST',
    body: payload,
  })
}

export function fetchMe(): Promise<User> {
  return apiRequest<User>('/me', { auth: true })
}
