import { apiRequest } from './client'

export function requestPasswordReset(email: string): Promise<{ message: string }> {
  return apiRequest('/auth/password-reset/request', {
    method: 'POST',
    data: { email },
  })
}

export function confirmPasswordReset(
  token: string,
  password: string,
): Promise<{ message: string }> {
  return apiRequest(`/auth/password-reset/${token}`, {
    method: 'POST',
    data: { password },
  })
}
