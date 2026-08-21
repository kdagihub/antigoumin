from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router

from core.auth.deps import jwt_auth
from core.models import InAppNotification

from .schemas import InAppNotificationSchema, NotificationReadResultSchema

router = Router(tags=["Notifications"])


@router.get("/", response=list[InAppNotificationSchema], auth=jwt_auth)
def list_notifications(request, unread_only: bool = False):
    notifications = InAppNotification.objects.filter(recipient=request.auth)
    if unread_only:
        notifications = notifications.filter(read_at__isnull=True)
    return list(notifications[:50])


@router.post(
    "/{notification_id}/read",
    response=NotificationReadResultSchema,
    auth=jwt_auth,
)
def mark_notification_read(request, notification_id: int):
    notification = get_object_or_404(
        InAppNotification,
        id=notification_id,
        recipient=request.auth,
    )
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return NotificationReadResultSchema(
        id=notification.id,
        read_at=notification.read_at,
    )
