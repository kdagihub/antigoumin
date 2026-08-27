import { apiRequest } from './client'

export interface Alliance {
  id: number
  declaration_id: number
  initiator_id: number
  partner_id: number
  initiator_name: string
  partner_name: string
  initiator_is_status_searchable: boolean
  partner_is_status_searchable: boolean
  status: 'PENDING_PARTNER' | 'ACTIVE' | 'REFUSED' | 'ENDED'
  initiator_badge_public: boolean
  partner_badge_public: boolean
  subscription_end_date: string | null
  created_at: string
}

export interface AllianceResult {
  id: number
  status: string
  message: string
}

export interface EligibleDeclaration {
  id: number
  partner_label: string
  relation_type: string
  role: 'initiator' | 'partner'
}

export function fetchAlliances(): Promise<Alliance[]> {
  return apiRequest<Alliance[]>('/alliances/')
}

export function fetchEligibleDeclarations(): Promise<EligibleDeclaration[]> {
  return apiRequest<EligibleDeclaration[]>('/alliances/eligible-declarations/')
}

export function decideAlliance(allianceId: number, accept: boolean): Promise<AllianceResult> {
  return apiRequest<AllianceResult>(`/alliances/${allianceId}/decision`, {
    method: 'POST',
    data: { accept },
  })
}

export function setAllianceBadge(allianceId: number, visible: boolean): Promise<Alliance> {
  return apiRequest<Alliance>(`/alliances/${allianceId}/badge`, {
    method: 'PATCH',
    data: { visible },
  })
}

export function endAlliance(allianceId: number): Promise<AllianceResult> {
  return apiRequest<AllianceResult>(`/alliances/${allianceId}/end`, {
    method: 'POST',
  })
}
