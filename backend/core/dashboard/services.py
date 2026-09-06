from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.db import models
from django.utils import timezone

from core.models import Alliance, Declaration, PhoneVerificationAccess, TransparencyRequest, User


@dataclass(frozen=True)
class DashboardStatItem:
    key: str
    value: int


@dataclass(frozen=True)
class DashboardActivityItem:
    type: str
    label: str
    occurred_at: datetime
    route: str


@dataclass(frozen=True)
class DashboardNextAction:
    code: str
    title: str
    description: str
    route: str


def _format_phone_display(phone: str) -> str:
    digits = phone
    if digits.startswith("225") and len(digits) >= 13:
        local = digits[3:]
        return f"{local[:2]} {local[2:4]} {local[4:6]} {local[6:8]} {local[8:10]}"
    return phone


def build_dashboard_stats(user: User) -> list[DashboardStatItem]:
    declarations = Declaration.objects.filter(author=user).count()
    verifications = PhoneVerificationAccess.objects.filter(
        user=user,
        used_at__isnull=False,
    ).count()
    active_alliances = Alliance.objects.filter(
        models.Q(initiator=user) | models.Q(partner=user),
        status=Alliance.Status.ACTIVE,
    ).count()
    transparency_requests = TransparencyRequest.objects.filter(requester=user).count()
    return [
        DashboardStatItem(key="declarations", value=declarations),
        DashboardStatItem(key="verifications", value=verifications),
        DashboardStatItem(key="active_alliances", value=active_alliances),
        DashboardStatItem(key="transparency_requests", value=transparency_requests),
    ]


def build_dashboard_activity(user: User, *, limit: int = 10) -> list[DashboardActivityItem]:
    items: list[DashboardActivityItem] = []

    for access in PhoneVerificationAccess.objects.filter(
        user=user,
        used_at__isnull=False,
    ).order_by("-used_at")[:limit]:
        phone_label = _format_phone_display(access.phone)
        items.append(
            DashboardActivityItem(
                type="verification",
                label=f"Vérification du numéro {phone_label}",
                occurred_at=access.used_at,
                route="/app/verification",
            )
        )

    for declaration in Declaration.objects.filter(author=user).order_by("-created_at")[:limit]:
        items.append(
            DashboardActivityItem(
                type="declaration",
                label=f"Déclaration envoyée à {declaration.partner_name}",
                occurred_at=declaration.created_at,
                route="/app/declarations",
            )
        )

    for request in TransparencyRequest.objects.filter(requester=user).order_by("-created_at")[:limit]:
        phone_label = _format_phone_display(request.target_phone)
        items.append(
            DashboardActivityItem(
                type="transparency",
                label=f"Demande de transparence vers {phone_label}",
                occurred_at=request.created_at,
                route="/app/transparence",
            )
        )

    for alliance in (
        Alliance.objects.filter(models.Q(initiator=user) | models.Q(partner=user))
        .select_related("initiator", "partner")
        .order_by("-created_at")[:limit]
    ):
        partner = alliance.partner if alliance.initiator_id == user.id else alliance.initiator
        partner_label = partner.full_name or partner.email
        if alliance.status == Alliance.Status.ACTIVE:
            label = f"Alliance active avec {partner_label}"
        elif alliance.status == Alliance.Status.PENDING_PARTNER:
            label = f"Alliance en attente avec {partner_label}"
        elif alliance.status == Alliance.Status.ENDED:
            label = f"Alliance terminée avec {partner_label}"
        else:
            label = f"Alliance avec {partner_label}"
        items.append(
            DashboardActivityItem(
                type="alliance",
                label=label,
                occurred_at=alliance.created_at,
                route="/app/alliances",
            )
        )

    items.sort(key=lambda item: item.occurred_at, reverse=True)
    return items[:limit]


def _has_eligible_alliance_declaration(user: User) -> bool:
    declarations = Declaration.objects.filter(
        status=Declaration.Status.VERIFIED,
        ended_at__isnull=True,
    ).filter(models.Q(author=user) | models.Q(accepted_by=user))
    if not declarations.exists():
        return False
    blocked = Alliance.objects.filter(
        declaration_id__in=declarations.values_list("id", flat=True),
        status__in=[Alliance.Status.PENDING_PARTNER, Alliance.Status.ACTIVE],
    ).exists()
    return not blocked


def build_next_action(user: User, stats: list[DashboardStatItem]) -> DashboardNextAction | None:
    stat_map = {item.key: item.value for item in stats}

    if not user.is_fully_verified:
        return DashboardNextAction(
            code="verify_account",
            title="Vérifiez votre compte",
            description=(
                "Confirmez votre email ou votre téléphone pour débloquer "
                "les vérifications, déclarations et alliances."
            ),
            route="/app/profil",
        )

    if stat_map.get("verifications", 0) == 0:
        return DashboardNextAction(
            code="first_verification",
            title="Vérifiez un premier numéro",
            description=(
                "Consultez discrètement le statut relationnel d'un numéro ivoirien. "
                "La personne ne sera pas alertée."
            ),
            route="/app/verification",
        )

    if stat_map.get("declarations", 0) == 0:
        return DashboardNextAction(
            code="first_declaration",
            title="Déclarez votre relation",
            description=(
                "Officialisez votre lien et invitez votre partenaire par SMS "
                "à confirmer en toute liberté."
            ),
            route="/app/declarations",
        )

    if stat_map.get("active_alliances", 0) == 0 and _has_eligible_alliance_declaration(user):
        return DashboardNextAction(
            code="create_alliance",
            title="Scellez votre Alliance Premium",
            description=(
                "Activez les alertes si votre partenaire est sollicité ou déclaré "
                "par un tiers — sans révéler qui."
            ),
            route="/app/abonnement",
        )

    if stat_map.get("transparency_requests", 0) == 0:
        return DashboardNextAction(
            code="first_transparency",
            title="Envoyer une demande de transparence",
            description=(
                "Invitez quelqu'un à clarifier son statut de façon identifiable "
                "et volontaire."
            ),
            route="/app/transparence",
        )

    return None


def build_dashboard_summary(user: User) -> dict:
    stats = build_dashboard_stats(user)
    activity = build_dashboard_activity(user)
    return {
        "stats": stats,
        "activity": activity,
        "next_action": build_next_action(user, stats),
    }
