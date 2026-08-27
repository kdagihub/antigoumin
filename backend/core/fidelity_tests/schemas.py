import secrets
from datetime import datetime

from ninja import Schema


class TransparencyRequestCreateSchema(Schema):
    target_phone: str
    payment_id: int | None = None


class TransparencyRequestSchema(Schema):
    id: int
    target_phone: str
    status: str
    expires_at: datetime
    respond_url: str


class TransparencyRequestListItemSchema(Schema):
    id: int
    target_phone: str
    status: str
    declared_status: str | None
    declared_partner_name: str | None
    expires_at: datetime
    responded_at: datetime | None
    created_at: datetime


class TransparencyRequestListSchema(Schema):
    items: list[TransparencyRequestListItemSchema]
    count: int


class TransparencyRequestPreviewSchema(Schema):
    requester_display_name: str
    status: str
    expires_at: datetime
    consent_notice: str


class TransparencyRequestRespondSchema(Schema):
    action: str
    declared_status: str | None = None
    declared_partner_name: str | None = None


class TransparencyRequestResultSchema(Schema):
    id: int
    status: str
    declared_status: str | None
    message: str
