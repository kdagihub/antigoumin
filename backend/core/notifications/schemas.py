from datetime import datetime
from typing import Any

from ninja import Schema


class InAppNotificationSchema(Schema):
    id: int
    type: str
    title: str
    message: str
    metadata: dict[str, Any]
    read_at: datetime | None
    created_at: datetime


class NotificationReadResultSchema(Schema):
    id: int
    read_at: datetime
