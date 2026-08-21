from datetime import datetime

from ninja import Schema


class AllianceSchema(Schema):
    id: int
    declaration_id: int
    initiator_id: int
    partner_id: int
    initiator_name: str
    partner_name: str
    initiator_is_status_searchable: bool
    partner_is_status_searchable: bool
    status: str
    initiator_badge_public: bool
    partner_badge_public: bool
    subscription_end_date: datetime | None
    created_at: datetime


class AllianceDecisionSchema(Schema):
    accept: bool


class AllianceBadgeSchema(Schema):
    visible: bool


class AllianceResultSchema(Schema):
    id: int
    status: str
    message: str
