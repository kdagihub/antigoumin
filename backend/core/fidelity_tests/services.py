import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from ninja.errors import HttpError

from core.models import TransparencyRequest, User
from core.notifications.email import notify_phone_or_user_email, notify_user_by_email
from core.notifications.sms import send_transparency_request_sms_async
from core.pricing import ServiceType
from core.subscriptions.quotas import can_use_vip_quota
from core.utils.phone import normalize_phone
from core.utils.subscription import get_unused_payment

from .schemas import (
    TransparencyRequestListItemSchema,
    TransparencyRequestPreviewSchema,
    TransparencyRequestResultSchema,
    TransparencyRequestSchema,
)


class TransparencyRequestServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def handle_transparency_request_error(exc: TransparencyRequestServiceError):
    raise HttpError(exc.status_code, exc.message)


def list_transparency_requests(user: User) -> list[TransparencyRequestListItemSchema]:
    requests = TransparencyRequest.objects.filter(requester=user).order_by("-created_at")
    return [
        TransparencyRequestListItemSchema(
            id=item.id,
            target_phone=item.target_phone,
            status=item.status,
            declared_status=item.declared_status or None,
            declared_partner_name=item.declared_partner_name or None,
            expires_at=item.expires_at,
            responded_at=item.responded_at,
            created_at=item.created_at,
        )
        for item in requests
    ]


def create_transparency_request(
    request,
    user: User,
    *,
    target_phone: str,
    payment_id: int | None = None,
) -> TransparencyRequestSchema:
    payment = get_unused_payment(
        user,
        ServiceType.TRANSPARENCY_REQUEST,
        payment_id=payment_id,
    )
    use_vip_quota = payment is None and can_use_vip_quota(user, ServiceType.TRANSPARENCY_REQUEST)
    if payment is None and not use_vip_quota and not settings.DEBUG:
        raise TransparencyRequestServiceError(
            402,
            "Paiement Demande de Transparence requis (550 FCFA).",
        )

    try:
        normalized_phone = normalize_phone(target_phone)
    except ValueError as exc:
        raise TransparencyRequestServiceError(400, str(exc)) from exc

    if user.phone_number and normalize_phone(user.phone_number) == normalized_phone:
        raise TransparencyRequestServiceError(
            400,
            "Vous ne pouvez pas vous envoyer une Demande de Transparence.",
        )

    if TransparencyRequest.objects.filter(
        requester=user,
        target_phone=normalized_phone,
        status=TransparencyRequest.Status.PENDING,
        expires_at__gt=timezone.now(),
    ).exists():
        raise TransparencyRequestServiceError(
            409,
            "Une demande est déjà active pour ce numéro.",
        )

    cooldown_since = timezone.now() - timedelta(
        hours=settings.TRANSPARENCY_REQUEST_COOLDOWN_HOURS
    )
    if TransparencyRequest.objects.filter(
        requester=user,
        target_phone=normalized_phone,
        created_at__gte=cooldown_since,
    ).exists():
        raise TransparencyRequestServiceError(
            429,
            "Veuillez attendre avant d'envoyer une nouvelle demande à ce numéro.",
        )

    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(
        hours=settings.TRANSPARENCY_REQUEST_TTL_HOURS
    )

    with transaction.atomic():
        transparency_request = TransparencyRequest.objects.create(
            requester=user,
            target_phone=normalized_phone,
            payment=payment,
            token=token,
            expires_at=expires_at,
        )
        if payment:
            payment.consumed = True
            payment.metadata = {
                **payment.metadata,
                "transparency_request_id": transparency_request.id,
            }
            payment.save(update_fields=["consumed", "metadata"])

    requester_name = user.full_name or user.email
    send_transparency_request_sms_async(
        normalized_phone,
        token,
        requester_name,
        expires_at,
    )
    respond_url = (
        f"{settings.FRONTEND_BASE_URL.rstrip('/')}/transparence/{token}"
    )
    notify_user_by_email(
        user.email,
        "Votre Demande de Transparence a été envoyée",
        (
            "Votre invitation identifiable a été transmise. "
            "Le destinataire peut accepter, refuser, ignorer, bloquer ou signaler."
        ),
    )
    notify_phone_or_user_email(
        normalized_phone,
        "Demande de Transparence AntiGoumin",
        (
            f"{requester_name} vous invite à clarifier votre statut. "
            f"Répondez ici : {respond_url}"
        ),
    )
    return TransparencyRequestSchema(
        id=transparency_request.id,
        target_phone=transparency_request.target_phone,
        status=transparency_request.status,
        expires_at=transparency_request.expires_at,
        respond_url=respond_url,
    )


def preview_transparency_request(token: str) -> TransparencyRequestPreviewSchema:
    transparency_request = _get_request(token)
    _expire_if_needed(transparency_request)
    return TransparencyRequestPreviewSchema(
        requester_display_name=(
            transparency_request.requester.full_name
            or transparency_request.requester.email
        ),
        status=transparency_request.status,
        expires_at=transparency_request.expires_at,
        consent_notice=(
            "Cette invitation est volontaire. Vous pouvez répondre, refuser, ignorer, "
            "bloquer l'auteur ou signaler un abus. Votre réponse restera privée et "
            "votre silence ne sera interprété comme aucune preuve."
        ),
    )


def respond_to_transparency_request(
    token: str,
    *,
    action: str,
    declared_status: str | None = None,
    declared_partner_name: str | None = None,
) -> TransparencyRequestResultSchema:
    transparency_request = _get_request(token)
    _expire_if_needed(transparency_request)
    if transparency_request.status != TransparencyRequest.Status.PENDING:
        raise TransparencyRequestServiceError(400, "Cette demande est déjà terminée.")

    action = action.upper()
    action_statuses = {
        "ACCEPT": TransparencyRequest.Status.ACCEPTED,
        "REFUSE": TransparencyRequest.Status.REFUSED,
        "BLOCK": TransparencyRequest.Status.BLOCKED,
        "REPORT": TransparencyRequest.Status.REPORTED,
    }
    if action not in action_statuses:
        raise TransparencyRequestServiceError(400, "Action de réponse invalide.")

    if action == "ACCEPT":
        if declared_status not in TransparencyRequest.DeclaredStatus.values:
            raise TransparencyRequestServiceError(
                400,
                "Le statut déclaré est obligatoire pour accepter.",
            )
        transparency_request.declared_status = declared_status
        transparency_request.declared_partner_name = (
            declared_partner_name or ""
        ).strip()

    transparency_request.status = action_statuses[action]
    transparency_request.responded_at = timezone.now()
    transparency_request.save(
        update_fields=[
            "status",
            "declared_status",
            "declared_partner_name",
            "responded_at",
        ]
    )

    messages = {
        "ACCEPT": "Votre réponse privée a été enregistrée.",
        "REFUSE": "La demande a été refusée. Aucun statut n'a été communiqué.",
        "BLOCK": "L'auteur a été bloqué pour cette demande.",
        "REPORT": "La demande a été signalée à l'équipe AntiGoumin.",
    }
    return TransparencyRequestResultSchema(
        id=transparency_request.id,
        status=transparency_request.status,
        declared_status=transparency_request.declared_status or None,
        message=messages[action],
    )


def _get_request(token: str) -> TransparencyRequest:
    try:
        return TransparencyRequest.objects.select_related("requester").get(token=token)
    except TransparencyRequest.DoesNotExist as exc:
        raise TransparencyRequestServiceError(404, "Demande introuvable.") from exc


def _expire_if_needed(transparency_request: TransparencyRequest) -> None:
    if (
        transparency_request.status == TransparencyRequest.Status.PENDING
        and timezone.now() > transparency_request.expires_at
    ):
        transparency_request.status = TransparencyRequest.Status.EXPIRED
        transparency_request.save(update_fields=["status"])
        raise TransparencyRequestServiceError(
            410,
            "Cette demande a expiré sans réponse. Cela ne constitue aucune preuve.",
        )
