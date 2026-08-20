from ninja import NinjaAPI

from core.auth.deps import jwt_auth
from core.auth.router import router as auth_router
from core.auth.schemas import UserSchema

api = NinjaAPI(
    title="AntiGoumin API",
    version="1.0.0",
    description="API du registre de confiance AntiGoumin",
)

api.add_router("/auth", auth_router)


@api.get("/health", tags=["Système"])
def health(request):
    return {"status": "ok"}


@api.get("/me", response=UserSchema, auth=jwt_auth, tags=["Auth"])
def me(request):
    user = request.auth
    return UserSchema(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        auth_provider=user.auth_provider,
        subscription_end_date=user.subscription_end_date,
    )
