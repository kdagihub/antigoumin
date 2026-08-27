from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from ninja.errors import HttpError

from core.models import Alliance, Declaration, Payment, User
from core.notifications.email import notify_user_by_email
from core.notifications.sms import send_alliance_ended_sms_async

from .schemas import AllianceResultSchema, AllianceSchema, EligibleDeclarationSchema


class AllianceServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def handle_alliance_error(exc: AllianceServiceError):
    raise HttpError(exc.status_code, exc.message)


def alliance_to_schema(alliance: Alliance) -> AllianceSchema:
    return AllianceSchema(
        id=alliance.id,
        declaration_id=alliance.declaration_id,
        initiator_id=alliance.initiator_id,
        partner_id=alliance.partner_id,
        initiator_name=alliance.initiator.full_name or alliance.initiator.email,
        partner_name=alliance.partner.full_name or alliance.partner.email,
        initiator_is_status_searchable=alliance.initiator.is_status_searchable,
        partner_is_status_searchable=alliance.partner.is_status_searchable,
        status=alliance.status,
        initiator_badge_public=alliance.initiator_badge_public,
        partner_badge_public=alliance.partner_badge_public,
        subscription_end_date=alliance.subscription_end_date,
        created_at=alliance.created_at,
    )


def list_eligible_declarations(user: User) -> list[EligibleDeclarationSchema]:
    declarations = (
        Declaration.objects.filter(
            status=Declaration.Status.VERIFIED,
            ended_at__isnull=True,
        )
        .filter(models.Q(author=user) | models.Q(accepted_by=user))
        .select_related("author", "accepted_by")
        .order_by("-created_at")
    )
    blocked_ids = set(
        Alliance.objects.filter(
            declaration_id__in=declarations.values_list("id", flat=True),
            status__in=[
                Alliance.Status.PENDING_PARTNER,
                Alliance.Status.ACTIVE,
            ],
        ).values_list("declaration_id", flat=True)
    )
    eligible: list[EligibleDeclarationSchema] = []
    for declaration in declarations:
        if declaration.id in blocked_ids:
            continue
        if declaration.author_id == user.id:
            partner_label = declaration.partner_name
            role = "initiator"
        else:
            partner_label = declaration.author.full_name or declaration.author.email
            role = "partner"
        eligible.append(
            EligibleDeclarationSchema(
                id=declaration.id,
                partner_label=partner_label,
                relation_type=declaration.relation_type,
                role=role,
            )
        )
    return eligible


def create_pending_alliance(
    user: User,
    payment: Payment,
    *,
    declaration_id: int,
) -> Alliance:
    try:
        declaration = Declaration.objects.select_related(
            "author",
            "accepted_by",
        ).get(
            id=declaration_id,
            status=Declaration.Status.VERIFIED,
            ended_at__isnull=True,
        )
    except Declaration.DoesNotExist as exc:
        raise AllianceServiceError(
            400,
            "Une relation mutuellement validée est requise pour créer une Alliance.",
        ) from exc

    partner = declaration.accepted_by
    if partner is None:
        partner = User.objects.filter(
            phone_number=declaration.partner_phone,
            is_active=True,
        ).first()
    if partner is None:
        raise AllianceServiceError(
            400,
            "Le partenaire doit disposer d'un compte AntiGoumin associé au numéro validé.",
        )

    if declaration.author_id == user.id:
        other_party = partner
    elif partner.id == user.id:
        other_party = declaration.author
    else:
        raise AllianceServiceError(
            403,
            "Seules les parties de la relation peuvent créer une Alliance.",
        )

    if Alliance.objects.filter(
        declaration=declaration,
        status__in=[
            Alliance.Status.PENDING_PARTNER,
            Alliance.Status.ACTIVE,
        ],
    ).exists():
        raise AllianceServiceError(
            409,
            "Une Alliance existe déjà pour cette relation.",
        )

    alliance = Alliance.objects.create(
        declaration=declaration,
        initiator=user,
        partner=other_party,
        payment=payment,
        status=Alliance.Status.PENDING_PARTNER,
        initiator_consented_at=timezone.now(),
    )
    notify_user_by_email(
        user.email,
        "Invitation Alliance Digitale envoyée",
        (
            f"Votre invitation d'Alliance a été transmise à "
            f"{other_party.full_name or other_party.email}. "
            "L'Alliance ne sera active qu'après son consentement."
        ),
    )
    notify_user_by_email(
        other_party.email,
        "Invitation Alliance Digitale AntiGoumin",
        (
            f"{user.full_name or user.email} vous invite à sceller une Alliance Digitale. "
            "Connectez-vous à AntiGoumin pour accepter ou refuser. "
            "Aucun badge n'est publié tant que vous n'avez pas consenti."
        ),
    )
    return alliance


def list_user_alliances(user: User) -> list[AllianceSchema]:
    alliances = (
        Alliance.objects.filter(
            models.Q(initiator=user) | models.Q(partner=user)
        )
        .select_related("declaration", "initiator", "partner")
        .order_by("-created_at")
    )
    return [alliance_to_schema(alliance) for alliance in alliances]


def decide_alliance(
    user: User,
    alliance_id: int,
    *,
    accept: bool,
) -> AllianceResultSchema:
    try:
        alliance = Alliance.objects.select_related(
            "initiator",
            "partner",
        ).get(id=alliance_id)
    except Alliance.DoesNotExist as exc:
        raise AllianceServiceError(404, "Alliance introuvable.") from exc

    if alliance.partner_id != user.id:
        raise AllianceServiceError(
            403,
            "Seul le partenaire invité peut répondre.",
        )
    if alliance.status != Alliance.Status.PENDING_PARTNER:
        raise AllianceServiceError(400, "Cette invitation a déjà été traitée.")

    if not accept:
        alliance.status = Alliance.Status.REFUSED
        alliance.partner_consented_at = timezone.now()
        alliance.save(update_fields=["status", "partner_consented_at"])
        notify_user_by_email(
            alliance.initiator.email,
            "Invitation Alliance refusée",
            "Votre invitation d'Alliance Digitale a été refusée. Aucun badge n'a été publié.",
        )
        return AllianceResultSchema(
            id=alliance.id,
            status=alliance.status,
            message="Invitation Alliance refusée. Aucun badge n'a été publié.",
        )

    now = timezone.now()
    end_date = now + timedelta(days=settings.SUBSCRIPTION_DURATION_DAYS)
    with transaction.atomic():
        alliance.status = Alliance.Status.ACTIVE
        alliance.partner_consented_at = now
        alliance.subscription_end_date = end_date
        alliance.save(
            update_fields=[
                "status",
                "partner_consented_at",
                "subscription_end_date",
            ]
        )
        for party in (alliance.initiator, alliance.partner):
            party.subscription_end_date = end_date
            party.save(update_fields=["subscription_end_date"])

    notify_user_by_email(
        alliance.initiator.email,
        "Alliance Digitale activée",
        "Votre Alliance Digitale est active par consentement mutuel. Le badge public reste optionnel.",
    )
    notify_user_by_email(
        alliance.partner.email,
        "Alliance Digitale activée",
        "Votre Alliance Digitale est active par consentement mutuel. Le badge public reste optionnel.",
    )

    return AllianceResultSchema(
        id=alliance.id,
        status=alliance.status,
        message=(
            "Alliance activée par consentement mutuel. "
            "Chaque partie choisit séparément d'afficher ou non son badge."
        ),
    )


def set_badge_visibility(
    user: User,
    alliance_id: int,
    *,
    visible: bool,
) -> AllianceSchema:
    alliance = _get_active_alliance_for_user(user, alliance_id)
    if alliance.initiator_id == user.id:
        alliance.initiator_badge_public = visible
        field = "initiator_badge_public"
    else:
        alliance.partner_badge_public = visible
        field = "partner_badge_public"
    alliance.save(update_fields=[field])

    user.alliance_badge_enabled = visible
    user.save(update_fields=["alliance_badge_enabled"])
    return alliance_to_schema(alliance)


def end_alliance(user: User, alliance_id: int) -> AllianceResultSchema:
    alliance = _get_active_alliance_for_user(user, alliance_id)
    now = timezone.now()
    alliance.status = Alliance.Status.ENDED
    alliance.ended_at = now
    alliance.initiator_badge_public = False
    alliance.partner_badge_public = False
    alliance.save(
        update_fields=[
            "status",
            "ended_at",
            "initiator_badge_public",
            "partner_badge_public",
        ]
    )
    for party in (alliance.initiator, alliance.partner):
        party.alliance_badge_enabled = False
        party.save(update_fields=["alliance_badge_enabled"])
        if party.phone_number:
            send_alliance_ended_sms_async(party.phone_number, now)
        notify_user_by_email(
            party.email,
            "Votre Alliance Digitale a pris fin",
            (
                f"L'Alliance Digitale a pris fin le {now.strftime('%d/%m/%Y %H:%M')}. "
                "Aucun motif ni autre statut relationnel n'est communiqué."
            ),
        )

    return AllianceResultSchema(
        id=alliance.id,
        status=alliance.status,
        message=(
            "L'Alliance a pris fin. La notification ne communique aucun motif "
            "ni aucune information sur une autre relation."
        ),
    )


def _get_active_alliance_for_user(user: User, alliance_id: int) -> Alliance:
    try:
        return Alliance.objects.select_related("initiator", "partner").get(
            models.Q(initiator=user) | models.Q(partner=user),
            id=alliance_id,
            status=Alliance.Status.ACTIVE,
        )
    except Alliance.DoesNotExist as exc:
        raise AllianceServiceError(404, "Alliance active introuvable.") from exc
