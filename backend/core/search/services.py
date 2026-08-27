from django.conf import settings
from django.db.models import Q
from ninja.errors import HttpError

from core.models import Declaration, User
from core.pricing import ServiceType
from core.utils.phone import normalize_phone
from core.utils.subscription import has_verification_access

from .schemas import SearchResponseSchema


class SearchServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def handle_search_error(exc: SearchServiceError):
    raise HttpError(exc.status_code, exc.message)


def _active_public_declaration_filter(user: User) -> Q:
    return Q(author=user) | Q(accepted_by=user)


def search_by_phone(request, user: User, phone: str) -> SearchResponseSchema:
    try:
        normalized_phone = normalize_phone(phone)
    except ValueError as exc:
        raise SearchServiceError(400, str(exc)) from exc

    price_fcfa = settings.SERVICE_PRICES[ServiceType.VERIFICATION]

    if not has_verification_access(user, normalized_phone):
        return SearchResponseSchema(
            phone=normalized_phone,
            certified_status="PAYMENT_REQUIRED",
            price_fcfa=price_fcfa,
        )

    target = User.objects.filter(
        phone_number=normalized_phone,
        is_active=True,
    ).first()
    if target is None:
        return SearchResponseSchema(
            phone=normalized_phone,
            certified_status="NOT_A_MEMBER",
            price_fcfa=price_fcfa,
        )

    if not target.is_status_searchable:
        return SearchResponseSchema(
            phone=normalized_phone,
            certified_status="STATUS_NOT_PUBLIC",
            price_fcfa=price_fcfa,
        )

    is_engaged = Declaration.objects.filter(
        _active_public_declaration_filter(target),
        status=Declaration.Status.VERIFIED,
        visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
        ended_at__isnull=True,
    ).exists()

    return SearchResponseSchema(
        phone=normalized_phone,
        certified_status="ENGAGED" if is_engaged else "REGISTERED_NO_DECLARATION",
        price_fcfa=price_fcfa,
    )
