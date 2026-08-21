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

export function fetchAlliances(): Promise<Alliance[]> {
  return apiRequest<Alliance[]>('/alliances/')
}
