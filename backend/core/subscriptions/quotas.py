from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from core.models import Declaration, PhoneVerificationAccess, TransparencyRequest, User
from core.pricing import ServiceType
from core.subscriptions.services import get_active_alliance_for_user

VIP_QUOTA_LIMITS: dict[ServiceType, int] = {
    ServiceType.VERIFICATION: 5,
    ServiceType.DECLARATION: 1,
    ServiceType.TRANSPARENCY_REQUEST: 1,
}


@dataclass(frozen=True)
class VipBillingWindow:
    period_start: datetime
    period_end: datetime


@dataclass(frozen=True)
class VipQuotaItem:
    service_type: str
    limit: int
    used: int
    remaining: int


def get_vip_billing_window(user: User) -> VipBillingWindow | None:
    alliance = get_active_alliance_for_user(user)
    if alliance is None or alliance.subscription_end_date is None:
        return None
    now = timezone.now()
    if alliance.subscription_end_date <= now:
        return None
    period_end = alliance.subscription_end_date
    period_start = period_end - timedelta(days=settings.SUBSCRIPTION_DURATION_DAYS)
    return VipBillingWindow(period_start=period_start, period_end=period_end)


def _count_vip_verifications(user: User, window: VipBillingWindow) -> int:
    return PhoneVerificationAccess.objects.filter(
        user=user,
        payment__isnull=True,
        used_at__gte=window.period_start,
        used_at__lt=window.period_end,
    ).count()


def _count_vip_declarations(user: User, window: VipBillingWindow) -> int:
    return Declaration.objects.filter(
        author=user,
        payment__isnull=True,
        created_at__gte=window.period_start,
        created_at__lt=window.period_end,
    ).count()


def _count_vip_transparency_requests(user: User, window: VipBillingWindow) -> int:
    return TransparencyRequest.objects.filter(
        requester=user,
        payment__isnull=True,
        created_at__gte=window.period_start,
        created_at__lt=window.period_end,
    ).count()


def count_vip_quota_usage(user: User, service_type: ServiceType) -> int:
    window = get_vip_billing_window(user)
    if window is None:
        return 0
    counters = {
        ServiceType.VERIFICATION: _count_vip_verifications,
        ServiceType.DECLARATION: _count_vip_declarations,
        ServiceType.TRANSPARENCY_REQUEST: _count_vip_transparency_requests,
    }
    counter = counters.get(service_type)
    if counter is None:
        return 0
    return counter(user, window)


def vip_quota_remaining(user: User, service_type: ServiceType) -> int:
    if get_vip_billing_window(user) is None:
        return 0
    limit = VIP_QUOTA_LIMITS.get(service_type, 0)
    if limit <= 0:
        return 0
    used = count_vip_quota_usage(user, service_type)
    return max(limit - used, 0)


def can_use_vip_quota(user: User, service_type: ServiceType) -> bool:
    return vip_quota_remaining(user, service_type) > 0


def build_vip_quota_status(user: User) -> dict:
    window = get_vip_billing_window(user)
    active = window is not None
    quotas: list[VipQuotaItem] = []
    for service_type, limit in VIP_QUOTA_LIMITS.items():
        used = count_vip_quota_usage(user, service_type) if active else 0
        quotas.append(
            VipQuotaItem(
                service_type=service_type.value,
                limit=limit,
                used=used,
                remaining=max(limit - used, 0),
            )
        )
    return {
        "active": active,
        "period_start": window.period_start if window else None,
        "period_end": window.period_end if window else None,
        "quotas": quotas,
    }
