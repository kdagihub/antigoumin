from django.db import models
from django.utils import timezone

from core.models import Alliance, User
from core.notifications.email import notify_user_by_email
from core.utils.phone import normalize_phone

PARTNER_DECLARED_ALERT_TITLE = "Alerte Alliance Digitale"
PARTNER_DECLARED_ALERT_MESSAGE = (
    "Votre partenaire vient d'être déclaré en relation avec une autre personne "
    "sur la plateforme. Veuillez lui demander plus d'informations sur cette démarche."
)

DECLARANT_PARTNER_ENGAGED_NOTICE = (
    "Ce partenaire est déjà engagé dans une Alliance Digitale VIP sur la plateforme. "
    "Vous pouvez tout de même envoyer votre déclaration : la personne invitée "
    "choisira librement d'accepter ou de refuser."
)


def partner_has_active_vip_alliance(phone: str) -> bool:
    return bool(_active_vip_alliances_for_phone(phone))


def declarant_partner_engagement_notice(phone: str) -> str:
    if partner_has_active_vip_alliance(phone):
        return DECLARANT_PARTNER_ENGAGED_NOTICE
    return ""


def _active_vip_alliances_for_phone(phone: str):
    try:
        normalized_phone = normalize_phone(phone)
    except ValueError:
        return Alliance.objects.none()

    partner_user = User.objects.filter(
        phone_number=normalized_phone,
        is_active=True,
    ).first()
    if partner_user is None:
        return Alliance.objects.none()

    now = timezone.now()
    return Alliance.objects.filter(
        models.Q(initiator=partner_user) | models.Q(partner=partner_user),
        status=Alliance.Status.ACTIVE,
        subscription_end_date__gt=now,
    ).select_related("initiator", "partner")


def _alliance_counterpart(alliance: Alliance, subject_user: User) -> User:
    if alliance.initiator_id == subject_user.id:
        return alliance.partner
    return alliance.initiator


def notify_alliance_partners_of_new_declaration(
    *,
    declared_partner_phone: str,
    declaration_id: int,
    exclude_user_id: int | None = None,
) -> int:
    """Alerte les membres d'une Alliance VIP active liés au numéro déclaré."""
    from core.models import InAppNotification

    notified = 0
    alliances = _active_vip_alliances_for_phone(declared_partner_phone)
    recipients: set[int] = set()

    for alliance in alliances:
        try:
            normalized_phone = normalize_phone(declared_partner_phone)
        except ValueError:
            continue
        subject_user = User.objects.filter(
            phone_number=normalized_phone,
            is_active=True,
        ).first()
        if subject_user is None:
            continue

        recipient = _alliance_counterpart(alliance, subject_user)
        if exclude_user_id and recipient.id == exclude_user_id:
            continue
        if recipient.id in recipients:
            continue
        recipients.add(recipient.id)

        InAppNotification.objects.create(
            recipient=recipient,
            type=InAppNotification.Type.PARTNER_DECLARED_BY_OTHER,
            title=PARTNER_DECLARED_ALERT_TITLE,
            message=PARTNER_DECLARED_ALERT_MESSAGE,
            metadata={
                "declaration_id": declaration_id,
                "alliance_id": alliance.id,
            },
        )
        notify_user_by_email(
            recipient.email,
            PARTNER_DECLARED_ALERT_TITLE,
            PARTNER_DECLARED_ALERT_MESSAGE,
        )
        notified += 1

    return notified
