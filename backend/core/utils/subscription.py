from django.utils import timezone

from django.db import models

from core.models import Alliance, Payment, PhoneVerificationAccess, User
from core.pricing import ServiceType


def has_alliance_vip(user: User) -> bool:
    return Alliance.objects.filter(
        models.Q(initiator=user) | models.Q(partner=user),
        status=Alliance.Status.ACTIVE,
        subscription_end_date__gt=timezone.now(),
    ).exists()


def has_verification_access(user: User, phone: str) -> bool:
    now = timezone.now()
    return PhoneVerificationAccess.objects.filter(
        user=user,
        phone=phone,
        expires_at__gt=now,
        used_at__isnull=True,
    ).exists()


def consume_verification_access(user: User, phone: str, *, result_status: str) -> None:
    """Marque l'accès payé comme consommé après affichage d'un résultat."""
    now = timezone.now()
    access = (
        PhoneVerificationAccess.objects.filter(
            user=user,
            phone=phone,
            expires_at__gt=now,
            used_at__isnull=True,
        )
        .select_related("payment")
        .order_by("-created_at")
        .first()
    )
    if access is None:
        return
    access.used_at = now
    access.result_status = result_status
    access.save(update_fields=["used_at", "result_status"])
    payment = access.payment
    if payment and not payment.consumed:
        payment.consumed = True
        payment.save(update_fields=["consumed"])


def get_unused_payment(user: User, service_type: ServiceType, *, payment_id: int | None) -> Payment | None:
    if payment_id is None:
        return None

    try:
        payment = Payment.objects.get(
            id=payment_id,
            user=user,
            service_type=service_type.value,
            status=Payment.Status.SUCCESS,
            consumed=False,
        )
    except Payment.DoesNotExist:
        return None
    return payment
