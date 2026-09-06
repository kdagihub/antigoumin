from datetime import datetime

from ninja import Schema


class VipQuotaItemSchema(Schema):
    service_type: str
    limit: int
    used: int
    remaining: int


class VipQuotaStatusSchema(Schema):
    active: bool
    period_start: datetime | None = None
    period_end: datetime | None = None
    quotas: list[VipQuotaItemSchema]
