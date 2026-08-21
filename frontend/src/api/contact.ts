import { apiRequest } from './client'

export type ContactDestination = 'contact' | 'privacy'

export interface ContactPayload {
  name: string
  email: string
  destination: ContactDestination
  message: string
  website?: string
}

export function submitContact(payload: ContactPayload): Promise<{ message: string }> {
  return apiRequest('/contact/', {
    method: 'POST',
    data: payload,
  })
}
