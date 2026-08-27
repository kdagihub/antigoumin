from django.conf import settings
from django.db.models import Q
from ninja.errors import HttpError

from core.models import Declaration, PhoneVerificationAccess, User
from core.pricing import ServiceType
from core.utils.phone import normalize_phone
from core.utils.subscription import consume_verification_access, has_verification_access

from .schemas import SearchResponseSchema, VerificationHistoryItemSchema


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
        response = SearchResponseSchema(
            phone=normalized_phone,
            certified_status="NOT_A_MEMBER",
            price_fcfa=price_fcfa,
        )
    elif not target.is_status_searchable:
        response = SearchResponseSchema(
            phone=normalized_phone,
            certified_status="STATUS_NOT_PUBLIC",
            price_fcfa=price_fcfa,
        )
    else:
        is_engaged = Declaration.objects.filter(
            _active_public_declaration_filter(target),
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            ended_at__isnull=True,
        ).exists()
        response = SearchResponseSchema(
            phone=normalized_phone,
            certified_status="ENGAGED" if is_engaged else "REGISTERED_NO_DECLARATION",
            price_fcfa=price_fcfa,
        )

    consume_verification_access(user, normalized_phone, result_status=response.certified_status)
    return response


def list_verification_history(user: User, *, limit: int = 20) -> list[VerificationHistoryItemSchema]:
    accesses = (
        PhoneVerificationAccess.objects.filter(user=user, used_at__isnull=False)
        .select_related("payment")
        .order_by("-used_at")[:limit]
    )
    return [
        VerificationHistoryItemSchema(
            id=access.id,
            phone=access.phone,
            certified_status=access.result_status or "UNKNOWN",
            amount_fcfa=access.payment.amount if access.payment_id else 0,
            consulted_at=access.used_at,
        )
        for access in accesses
        if access.used_at is not None
    ]
