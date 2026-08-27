import { apiRequest } from './client'

export type CertifiedStatus =
  | 'PAYMENT_REQUIRED'
  | 'NOT_A_MEMBER'
  | 'REGISTERED_NO_DECLARATION'
  | 'ENGAGED'
  | 'STATUS_NOT_PUBLIC'

export interface SearchResult {
  phone: string
  certified_status: CertifiedStatus
  price_fcfa: number
}

export function searchByPhone(phone: string): Promise<SearchResult> {
  const params = new URLSearchParams({ phone })
  return apiRequest(`/search/?${params.toString()}`)
}
