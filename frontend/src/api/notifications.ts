import { apiRequest } from './client'

export interface InAppNotification {
  id: number
  type: string
  title: string
  message: string
  metadata: Record<string, unknown>
  read_at: string | null
  created_at: string
}

export function fetchUnreadNotifications(): Promise<InAppNotification[]> {
  return apiRequest<InAppNotification[]>('/notifications/?unread_only=true')
}

export function markNotificationRead(
  notificationId: number,
): Promise<{ id: number; read_at: string }> {
  return apiRequest(`/notifications/${notificationId}/read`, {
    method: 'POST',
  })
}
