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
  included_in_vip?: boolean
  vip_quota_remaining?: number | null
}

export interface VerificationHistoryItem {
  id: number
  phone: string
  certified_status: Exclude<CertifiedStatus, 'PAYMENT_REQUIRED'>
  amount_fcfa: number
  included_in_vip?: boolean
  consulted_at: string
}

export interface VerificationHistoryList {
  items: VerificationHistoryItem[]
  count: number
}

export function searchByPhone(phone: string): Promise<SearchResult> {
  const params = new URLSearchParams({ phone })
  return apiRequest(`/search/?${params.toString()}`)
}

export function fetchVerificationHistory(): Promise<VerificationHistoryList> {
  return apiRequest('/search/history/')
}
