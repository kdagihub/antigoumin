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

export interface TransparencyResponsePayload {
  action: 'ACCEPT' | 'REFUSE' | 'BLOCK' | 'REPORT'
  declared_status?: 'ENGAGED' | 'AVAILABLE' | 'PREFER_NOT_TO_ANSWER'
  declared_partner_name?: string
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
