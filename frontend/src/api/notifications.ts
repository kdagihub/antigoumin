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

export function fetchNotifications(unreadOnly = false): Promise<InAppNotification[]> {
  const params = new URLSearchParams()
  if (unreadOnly) {
    params.set('unread_only', 'true')
  }
  const query = params.toString()
  return apiRequest<InAppNotification[]>(`/notifications/${query ? `?${query}` : ''}`)
}

export function fetchUnreadNotifications(): Promise<InAppNotification[]> {
  return fetchNotifications(true)
}

export function markNotificationRead(
  notificationId: number,
): Promise<{ id: number; read_at: string }> {
  return apiRequest(`/notifications/${notificationId}/read`, {
    method: 'POST',
  })
}
