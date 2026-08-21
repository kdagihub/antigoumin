import { apiRequest } from './client'

export interface DeclarationPreview {
  partner_name: string
  author_name: string
  relation_type: string
  visibility: 'PRIVATE' | 'PUBLIC_CERTIFIED'
  consent_notice: string
  status: string
  expires_in_minutes: number
}

export interface DeclarationDecision {
  declaration_id: number
  status: string
  message: string
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
