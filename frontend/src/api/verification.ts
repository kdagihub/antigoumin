import { apiRequest } from './client'
import type { User } from '@/types/user'

export function resendEmailVerification(): Promise<{ message: string }> {
  return apiRequest('/auth/resend-email-verification', { method: 'POST' })
}

export function updateEmail(email: string): Promise<User> {
  return apiRequest('/auth/me/email', {
    method: 'PATCH',
    data: { email },
  })
}

export function verifyEmailToken(token: string): Promise<User> {
  return apiRequest(`/auth/verify-email/${token}`, { method: 'POST' })
}

export function updatePhone(phoneNumber: string): Promise<User> {
  return apiRequest('/auth/me/phone', {
    method: 'PATCH',
    data: { phone_number: phoneNumber },
  })
}

export function sendPhoneOtp(): Promise<{ message: string }> {
  return apiRequest('/auth/phone/send-otp', { method: 'POST' })
}

export function verifyPhoneOtp(code: string): Promise<User> {
  return apiRequest('/auth/phone/verify', {
    method: 'POST',
    data: { code },
  })
}
