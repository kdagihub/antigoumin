import { apiRequest } from './client'

export interface TransparencyRequestPreview {
  requester_display_name: string
  status: string
  expires_at: string
  consent_notice: string
}

export interface TransparencyRequestResponse {
  id: number
  status: string
  declared_status: string | null
  message: string
}

export interface TransparencyRequest {
  id: number
  target_phone: string
  status: string
  declared_status: string | null
  declared_partner_name: string | null
  expires_at: string
  responded_at: string | null
  created_at: string
}

export interface TransparencyRequestList {
  items: TransparencyRequest[]
  count: number
}

export interface TransparencyRequestCreated {
  id: number
  target_phone: string
  status: string
  expires_at: string
  respond_url: string
}

export interface TransparencyResponsePayload {
  action: 'ACCEPT' | 'REFUSE' | 'BLOCK' | 'REPORT'
  declared_status?: 'ENGAGED' | 'AVAILABLE' | 'PREFER_NOT_TO_ANSWER'
  declared_partner_name?: string
}

export function fetchTransparencyRequests(): Promise<TransparencyRequestList> {
  return apiRequest<TransparencyRequestList>('/transparency-requests/')
}

export function createTransparencyRequest(payload: {
  target_phone: string
  payment_id?: number
}): Promise<TransparencyRequestCreated> {
  return apiRequest<TransparencyRequestCreated>('/transparency-requests/', {
    method: 'POST',
    data: payload,
  })
}

export function fetchTransparencyRequest(token: string): Promise<TransparencyRequestPreview> {
  return apiRequest<TransparencyRequestPreview>(`/transparency-requests/${token}`)
}

export function respondToTransparencyRequest(
  token: string,
  payload: TransparencyResponsePayload,
): Promise<TransparencyRequestResponse> {
  return apiRequest<TransparencyRequestResponse>(`/transparency-requests/${token}/respond`, {
    method: 'POST',
    data: payload,
  })
}
