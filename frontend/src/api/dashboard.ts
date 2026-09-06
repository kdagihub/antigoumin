import { apiRequest } from './client'

export interface DashboardStat {
  key: 'declarations' | 'verifications' | 'active_alliances' | 'transparency_requests'
  value: number
}

export interface DashboardActivityItem {
  type: 'verification' | 'declaration' | 'transparency' | 'alliance'
  label: string
  occurred_at: string
  route: string
}

export interface DashboardNextAction {
  code: string
  title: string
  description: string
  route: string
}

export interface DashboardSummary {
  stats: DashboardStat[]
  activity: DashboardActivityItem[]
  next_action: DashboardNextAction | null
}

export function fetchDashboardSummary(): Promise<DashboardSummary> {
  return apiRequest('/dashboard/summary/')
}
