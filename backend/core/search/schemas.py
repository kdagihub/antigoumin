from ninja import Schema
from datetime import datetime


class SearchResponseSchema(Schema):
    phone: str
    certified_status: str
    price_fcfa: int


class VerificationHistoryItemSchema(Schema):
    id: int
    phone: str
    certified_status: str
    amount_fcfa: int
    consulted_at: datetime


class VerificationHistoryListSchema(Schema):
    items: list[VerificationHistoryItemSchema]
    count: int
