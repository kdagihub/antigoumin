from datetime import datetime

from ninja import Schema


class DeclarationSchema(Schema):
    id: int
    partner_phone: str
    partner_name: str
    partner_photo: str | None
    relation_type: str
    visibility: str
    status: str
    created_at: datetime


class DeclarationListSchema(Schema):
    items: list[DeclarationSchema]
    count: int


class PartnerPreviewSchema(Schema):
    partner_phone: str
    price_fcfa: int
    consent_notice: str
    partner_in_active_alliance: bool = False
    partner_alliance_notice: str = ""


class VerifyPreviewSchema(Schema):
    partner_name: str
    author_name: str
    relation_type: str
    visibility: str
    consent_notice: str
    status: str
    expires_in_minutes: int


class VerifyResultSchema(Schema):
    declaration_id: int
    status: str
    message: str
