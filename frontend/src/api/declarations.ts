import { apiRequest } from './client'

export type RelationType = 'AMOUR' | 'FLIRT' | 'FIANCE' | 'MARIAGE'
export type DeclarationVisibility = 'PRIVATE' | 'PUBLIC_CERTIFIED'
export type DeclarationStatus = 'PENDING' | 'VERIFIED' | 'REJECTED' | 'ENDED'

export interface Declaration {
  id: number
  partner_phone: string
  partner_name: string
  partner_photo: string | null
  relation_type: RelationType
  visibility: DeclarationVisibility
  status: DeclarationStatus
  created_at: string
}

export interface DeclarationList {
  items: Declaration[]
  count: number
}

export interface PartnerPreview {
  partner_phone: string
  price_fcfa: number
  consent_notice: string
  partner_in_active_alliance: boolean
  partner_alliance_notice: string
}

export interface DeclarationPreview {
  partner_name: string
  author_name: string
  relation_type: string
  visibility: DeclarationVisibility
  consent_notice: string
  status: string
  expires_in_minutes: number
}

export interface DeclarationDecision {
  declaration_id: number
  status: string
  message: string
}

export interface CreateDeclarationPayload {
  partner_phone: string
  partner_name: string
  partner_photo: File
  relation_type: RelationType
  visibility: DeclarationVisibility
  payment_id?: number
}

export function fetchDeclarations(): Promise<DeclarationList> {
  return apiRequest('/declarations/')
}

export function fetchPartnerPreview(phone: string): Promise<PartnerPreview> {
  const params = new URLSearchParams({ phone })
  return apiRequest(`/declarations/partner-preview?${params.toString()}`)
}

export function createDeclaration(payload: CreateDeclarationPayload): Promise<Declaration> {
  const form = new FormData()
  form.append('partner_phone', payload.partner_phone)
  form.append('partner_name', payload.partner_name)
  form.append('partner_photo', payload.partner_photo)
  form.append('relation_type', payload.relation_type)
  form.append('visibility', payload.visibility)
  if (payload.payment_id) {
    form.append('payment_id', String(payload.payment_id))
  }
  return apiRequest('/declarations/', {
    method: 'POST',
    data: form,
  })
}

export function endDeclaration(declarationId: number): Promise<DeclarationDecision> {
  return apiRequest(`/declarations/${declarationId}/end`, { method: 'POST' })
}

export function fetchDeclarationPreview(token: string): Promise<DeclarationPreview> {
  return apiRequest<DeclarationPreview>(`/declarations/verify/${token}`)
}

export function decideDeclaration(
  token: string,
  accept: boolean,
): Promise<DeclarationDecision> {
  return apiRequest<DeclarationDecision>(
    `/declarations/verify/${token}/${accept ? 'accept' : 'reject'}`,
    { method: 'POST' },
  )
}
