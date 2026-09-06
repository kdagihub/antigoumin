from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from core.models import Alliance, InAppNotification, Payment, User
from core.notifications.email import notify_user_by_email

REMINDER_DAYS = (7, 3, 1)


class SubscriptionServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def get_active_alliance_for_user(user: User) -> Alliance | None:
    return (
        Alliance.objects.filter(
            models.Q(initiator=user) | models.Q(partner=user),
            status=Alliance.Status.ACTIVE,
        )
        .select_related("initiator", "partner", "declaration")
        .order_by("-created_at")
        .first()
    )


def renew_alliance_subscription(
    user: User,
    alliance_id: int,
    payment: Payment,
) -> timezone.datetime:
    try:
        alliance = Alliance.objects.select_related("initiator", "partner").get(
            id=alliance_id,
            status=Alliance.Status.ACTIVE,
        )
    except Alliance.DoesNotExist as exc:
        raise SubscriptionServiceError(
            404,
            "Alliance active introuvable pour ce renouvellement.",
        ) from exc

    if user.id not in {alliance.initiator_id, alliance.partner_id}:
        raise SubscriptionServiceError(
            403,
            "Vous ne pouvez renouveler que votre propre Alliance.",
        )

    now = timezone.now()
    current_end = alliance.subscription_end_date
    base = current_end if current_end and current_end > now else now
    end_date = base + timedelta(days=settings.SUBSCRIPTION_DURATION_DAYS)

    with transaction.atomic():
        alliance.subscription_end_date = end_date
        alliance.save(update_fields=["subscription_end_date"])
        for party in (alliance.initiator, alliance.partner):
            party.subscription_end_date = end_date
            party.save(update_fields=["subscription_end_date"])
        payment.consumed = True
        payment.metadata = {
            **(payment.metadata or {}),
            "renewal": True,
            "alliance_id": alliance.id,
        }
        payment.save(update_fields=["consumed", "metadata"])

    end_label = end_date.strftime("%d/%m/%Y")
    for party in (alliance.initiator, alliance.partner):
        InAppNotification.objects.create(
            recipient=party,
            type=InAppNotification.Type.SUBSCRIPTION_RENEWED,
            title="Abonnement Premium renouvelé",
            message=f"Votre Alliance Premium est active jusqu'au {end_label}.",
            metadata={"alliance_id": alliance.id, "subscription_end_date": end_date.isoformat()},
        )
        notify_user_by_email(
            party.email,
            "Abonnement Alliance Premium renouvelé",
            (
                f"Votre abonnement Alliance Digitale Premium a été renouvelé. "
                f"Il reste actif jusqu'au {end_label}."
            ),
        )

    return end_date


def _days_until(end_date: timezone.datetime, *, now: timezone.datetime | None = None) -> int:
    reference = now or timezone.now()
    return (end_date.date() - reference.date()).days


def _reminder_already_sent(
    user: User,
    *,
    days_before: int,
    subscription_end_date: timezone.datetime,
) -> bool:
    end_key = subscription_end_date.date().isoformat()
    return InAppNotification.objects.filter(
        recipient=user,
        type=InAppNotification.Type.SUBSCRIPTION_EXPIRING,
        metadata__days_before=days_before,
        metadata__subscription_end_date=end_key,
    ).exists()


def _expiration_already_processed(alliance: Alliance) -> bool:
    end_key = alliance.subscription_end_date.date().isoformat() if alliance.subscription_end_date else ""
    return InAppNotification.objects.filter(
        type=InAppNotification.Type.SUBSCRIPTION_EXPIRED,
        metadata__alliance_id=alliance.id,
        metadata__subscription_end_date=end_key,
    ).exists()


def _notify_expiring(user: User, *, days_before: int, end_date: timezone.datetime) -> None:
    end_label = end_date.strftime("%d/%m/%Y")
    if days_before == 1:
        body = f"Votre Premium expire demain ({end_label}). Renouvelez pour garder vos alertes Alliance."
    else:
        body = (
            f"Votre Premium expire dans {days_before} jours ({end_label}). "
            "Renouvelez depuis votre espace abonnement."
        )
    InAppNotification.objects.create(
        recipient=user,
        type=InAppNotification.Type.SUBSCRIPTION_EXPIRING,
        title="Votre Premium expire bientôt",
        message=body,
        metadata={
            "days_before": days_before,
            "subscription_end_date": end_date.date().isoformat(),
        },
    )
    notify_user_by_email(
        user.email,
        "Votre abonnement Alliance Premium expire bientôt",
        f"{body}\n\nConnectez-vous à AntiGoumin → Service Premium → Renouveler.",
    )


def send_subscription_expiry_reminders() -> int:
    now = timezone.now()
    sent = 0
    alliances = Alliance.objects.filter(
        status=Alliance.Status.ACTIVE,
        subscription_end_date__gt=now,
    ).select_related("initiator", "partner")

    for alliance in alliances:
        if alliance.subscription_end_date is None:
            continue
        days_left = _days_until(alliance.subscription_end_date, now=now)
        if days_left not in REMINDER_DAYS:
            continue
        for party in (alliance.initiator, alliance.partner):
            if _reminder_already_sent(
                party,
                days_before=days_left,
                subscription_end_date=alliance.subscription_end_date,
            ):
                continue
            _notify_expiring(party, days_before=days_left, end_date=alliance.subscription_end_date)
            sent += 1
    return sent


def expire_lapsed_subscriptions() -> int:
    now = timezone.now()
    processed = 0
    alliances = Alliance.objects.filter(
        status=Alliance.Status.ACTIVE,
        subscription_end_date__lt=now,
    ).select_related("initiator", "partner")

    for alliance in alliances:
        if _expiration_already_processed(alliance):
            continue
        end_date = alliance.subscription_end_date
        end_label = end_date.strftime("%d/%m/%Y") if end_date else ""

        with transaction.atomic():
            alliance.initiator_badge_public = False
            alliance.partner_badge_public = False
            alliance.save(
                update_fields=["initiator_badge_public", "partner_badge_public"]
            )
            for party in (alliance.initiator, alliance.partner):
                party.alliance_badge_enabled = False
                if not party.is_status_searchable:
                    party.is_status_searchable = True
                party.save(
                    update_fields=["alliance_badge_enabled", "is_status_searchable"]
                )
                InAppNotification.objects.create(
                    recipient=party,
                    type=InAppNotification.Type.SUBSCRIPTION_EXPIRED,
                    title="Abonnement Premium expiré",
                    message=(
                        "Votre Premium a expiré. Renouvelez pour réactiver vos alertes Alliance "
                        "et la gestion de votre visibilité."
                    ),
                    metadata={
                        "alliance_id": alliance.id,
                        "subscription_end_date": end_date.date().isoformat() if end_date else "",
                    },
                )
                notify_user_by_email(
                    party.email,
                    "Votre abonnement Alliance Premium a expiré",
                    (
                        f"Votre abonnement Alliance Digitale Premium a expiré le {end_label}. "
                        "Renouvelez depuis Service Premium pour retrouver vos alertes et avantages."
                    ),
                )
        processed += 1
    return processed


def process_subscriptions_daily() -> dict[str, int]:
    return {
        "reminders_sent": send_subscription_expiry_reminders(),
        "alliances_expired": expire_lapsed_subscriptions(),
    }
