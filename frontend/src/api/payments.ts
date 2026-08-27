import { apiRequest } from './client'

export interface CheckoutPayload {
  service_type: 'VERIFICATION' | 'DECLARATION' | 'TRANSPARENCY_REQUEST' | 'ALLIANCE_VIP'
  phone?: string
  declaration_id?: number
}

export interface CheckoutResponse {
  checkout_url: string
  reference: string
  amount: number
  service_type: string
}

export interface CheckoutStatus {
  reference: string
  status: string
  service_type: string
  credited: boolean
  message: string
  phone?: string
}

export function createCheckout(payload: CheckoutPayload): Promise<CheckoutResponse> {
  return apiRequest('/payments/checkout/', {
    method: 'POST',
    data: payload,
  })
}

export function fetchCheckoutStatus(reference: string): Promise<CheckoutStatus> {
  return apiRequest(`/payments/status/${reference}`)
}
