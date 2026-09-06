import { apiRequest } from './client'

export interface VipQuotaItem {
  service_type: 'VERIFICATION' | 'DECLARATION' | 'TRANSPARENCY_REQUEST'
  limit: number
  used: number
  remaining: number
}

export interface VipQuotaStatus {
  active: boolean
  period_start: string | null
  period_end: string | null
  quotas: VipQuotaItem[]
}

export function fetchVipQuotaStatus(): Promise<VipQuotaStatus> {
  return apiRequest('/subscriptions/vip-quota/')
}

export function getVipQuotaItem(
  status: VipQuotaStatus | null,
  serviceType: VipQuotaItem['service_type'],
): VipQuotaItem | null {
  if (!status?.active) return null
  return status.quotas.find((item) => item.service_type === serviceType) ?? null
}
