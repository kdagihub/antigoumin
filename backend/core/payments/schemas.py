from datetime import datetime

from ninja import Schema


class PaymentWebhookSchema(Schema):
    reference: str
    status: str
    service_type: str
    amount: int
    user_id: int
    metadata: dict = {}


class PaymentWebhookResponseSchema(Schema):
    ok: bool
    service_type: str
    subscription_end_date: datetime | None = None
    message: str


class CheckoutCreateSchema(Schema):
    service_type: str
    phone: str = ""
    declaration_id: int | None = None
    renewal: bool = False


class CheckoutResponseSchema(Schema):
    checkout_url: str
    reference: str
    amount: int
    service_type: str


class CheckoutStatusSchema(Schema):
    reference: str
    status: str
    service_type: str
    credited: bool
    message: str
    phone: str = ""
    payment_id: int | None = None


class UnusedPaymentSchema(Schema):
    payment_id: int | None = None
    service_type: str
