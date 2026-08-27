from ninja import Router

from core.auth.deps import jwt_verified_auth

from .schemas import (
    CheckoutCreateSchema,
    CheckoutResponseSchema,
    CheckoutStatusSchema,
    PaymentWebhookResponseSchema,
    PaymentWebhookSchema,
    UnusedPaymentSchema,
)
from .services import (
    PaymentServiceError,
    create_checkout,
    get_checkout_status,
    get_unused_payment_for_user,
    handle_payment_error,
    process_payment_webhook,
    verify_webhook_secret,
)

router = Router(tags=["Paiements"])


@router.post("/checkout/", response=CheckoutResponseSchema, auth=jwt_verified_auth)
def start_checkout(request, payload: CheckoutCreateSchema):
    try:
        return create_checkout(
            request.auth,
            service_type=payload.service_type,
            phone=payload.phone,
            declaration_id=payload.declaration_id,
        )
    except PaymentServiceError as exc:
        handle_payment_error(exc)


@router.get(
    "/status/{reference}",
    response=CheckoutStatusSchema,
    auth=jwt_verified_auth,
)
def checkout_status(request, reference: str):
    try:
        return get_checkout_status(request.auth, reference)
    except PaymentServiceError as exc:
        handle_payment_error(exc)


@router.get("/unused/", response=UnusedPaymentSchema, auth=jwt_verified_auth)
def unused_payment(request, service_type: str):
    try:
        return get_unused_payment_for_user(request.auth, service_type)
    except PaymentServiceError as exc:
        handle_payment_error(exc)


@router.post("/webhook/", response=PaymentWebhookResponseSchema)
def payment_webhook(request, payload: PaymentWebhookSchema):
    try:
        verify_webhook_secret(request)
        return process_payment_webhook(
            reference=payload.reference,
            status=payload.status,
            service_type=payload.service_type,
            amount=payload.amount,
            user_id=payload.user_id,
            metadata=payload.metadata,
        )
    except PaymentServiceError as exc:
        handle_payment_error(exc)
