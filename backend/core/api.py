from ninja import NinjaAPI

from core.auth.deps import jwt_auth
from core.alliances.router import router as alliances_router
from core.auth.router import router as auth_router
from core.auth.schemas import UserSchema
from core.catalog.router import router as catalog_router
from core.contact.router import router as contact_router
from core.declarations.router import router as declarations_router
from core.notifications.router import router as notifications_router
from core.fidelity_tests.router import router as transparency_requests_router
from core.payments.router import router as payments_router
from core.search.router import router as search_router

api = NinjaAPI(
    title="AntiGoumin API",
    version="1.0.0",
    description="API du registre de confiance AntiGoumin",
)

api.add_router("/auth", auth_router)
api.add_router("/alliances", alliances_router)
api.add_router("/catalog", catalog_router)
api.add_router("/contact", contact_router)
api.add_router("/declarations", declarations_router)
api.add_router("/notifications", notifications_router)
api.add_router("/search", search_router)
api.add_router("/payments", payments_router)
api.add_router("/transparency-requests", transparency_requests_router)


@api.get("/health", tags=["Système"])
def health(request):
    return {"status": "ok"}


@api.get("/me", response=UserSchema, auth=jwt_auth, tags=["Auth"])
def me(request):
    user = request.auth
    from core.utils.subscription import has_alliance_vip

    return UserSchema(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        auth_provider=user.auth_provider,
        subscription_end_date=user.subscription_end_date,
        alliance_badge_enabled=user.alliance_badge_enabled,
        is_status_searchable=user.is_status_searchable,
        email_verified=user.email_verified,
        phone_verified=user.phone_verified,
        is_fully_verified=user.is_fully_verified,
        has_alliance_vip=has_alliance_vip(user),
    )
