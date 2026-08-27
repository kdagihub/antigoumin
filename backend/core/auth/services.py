from django.conf import settings
from django.contrib.auth import authenticate
from django.db import models
from django.utils import timezone
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from ninja.errors import HttpError

from core.models import Alliance, Declaration, InAppNotification, User
from core.notifications.email import notify_user_by_email
from core.utils.phone import normalize_phone
from core.utils.subscription import has_alliance_vip

from core.utils.subscription import has_alliance_vip

from .jwt import create_access_token
from .schemas import TokenResponse, UserSchema


class AuthServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def user_to_schema(user: User) -> UserSchema:
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


def build_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=user_to_schema(user),
    )


def set_status_searchability(
    user: User,
    *,
    is_status_searchable: bool,
) -> UserSchema:
    if not is_status_searchable and not has_alliance_vip(user):
        raise AuthServiceError(
            403,
            "Seuls les membres Alliance Digitale VIP peuvent masquer "
            "leur statut consultable.",
        )
    visibility_was_removed = (
        user.is_status_searchable and not is_status_searchable
    )
    user.is_status_searchable = is_status_searchable
    user.save(update_fields=["is_status_searchable"])
    if visibility_was_removed:
        active_alliances = Alliance.objects.filter(
            models.Q(initiator=user) | models.Q(partner=user),
            status=Alliance.Status.ACTIVE,
            subscription_end_date__gt=timezone.now(),
        ).select_related("initiator", "partner")
        actor_name = user.full_name or "Votre partenaire"
        for alliance in active_alliances:
            partner = (
                alliance.partner
                if alliance.initiator_id == user.id
                else alliance.initiator
            )
            InAppNotification.objects.create(
                recipient=partner,
                type=InAppNotification.Type.PARTNER_VISIBILITY_DISABLED,
                title="Visibilité de votre partenaire modifiée",
                message=(
                    f"{actor_name} a désactivé la consultabilité publique "
                    "de son statut. Votre Alliance reste active."
                ),
                metadata={
                    "alliance_id": alliance.id,
                    "partner_visibility": "NOT_VISIBLE",
                },
            )
            notify_user_by_email(
                partner.email,
                "Visibilité de votre partenaire modifiée",
                (
                    f"{actor_name} a désactivé la consultabilité publique de son statut. "
                    "Votre Alliance Digitale reste active."
                ),
            )
    return user_to_schema(user)


def register_user(
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    phone_number: str = "",
) -> TokenResponse:
    email = User.objects.normalize_email(email)

    if User.objects.filter(email=email).exists():
        raise AuthServiceError(400, "Un compte existe déjà avec cet email.")
    if not phone_number:
        raise AuthServiceError(400, "Le numéro de téléphone est obligatoire.")
    try:
        normalized_phone = normalize_phone(phone_number)
    except ValueError as exc:
        raise AuthServiceError(400, str(exc)) from exc
    if User.objects.filter(phone_number=normalized_phone).exists():
        raise AuthServiceError(400, "Un compte utilise déjà ce numéro.")

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone_number=normalized_phone,
        is_status_searchable=True,
        auth_provider=User.AuthProvider.EMAIL,
    )
    from .verification import send_email_verification

    send_email_verification(user)
    return build_token_response(user)


def login_user(email: str, password: str) -> TokenResponse:
    user = authenticate(username=email, password=password)

    if user is None:
        existing = User.objects.filter(email=User.objects.normalize_email(email)).first()
        if existing and existing.auth_provider == User.AuthProvider.GOOGLE:
            raise AuthServiceError(
                400,
                "Ce compte utilise la connexion Google. Connectez-vous avec Google.",
            )
        raise AuthServiceError(401, "Email ou mot de passe incorrect.")

    if not user.is_active:
        raise AuthServiceError(403, "Ce compte est désactivé.")

    return build_token_response(user)


def authenticate_google(id_token: str) -> TokenResponse:
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise AuthServiceError(500, "Google OAuth n'est pas configuré sur le serveur.")

    try:
        payload = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except ValueError as exc:
        raise AuthServiceError(401, "Token Google invalide.") from exc

    google_id = payload.get("sub")
    email = payload.get("email")

    if not google_id or not email:
        raise AuthServiceError(401, "Token Google incomplet.")

    if not payload.get("email_verified", False):
        raise AuthServiceError(401, "L'email Google n'est pas vérifié.")

    email = User.objects.normalize_email(email)
    first_name = payload.get("given_name", "")
    last_name = payload.get("family_name", "")

    user = User.objects.filter(google_id=google_id).first()
    if user:
        if not user.email_verified_at:
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])
        return build_token_response(user)

    user = User.objects.filter(email=email).first()
    if user:
        if user.auth_provider == User.AuthProvider.EMAIL and not user.google_id:
            user.google_id = google_id
            user.auth_provider = User.AuthProvider.GOOGLE
            if not user.first_name:
                user.first_name = first_name
            if not user.last_name:
                user.last_name = last_name
            if not user.email_verified_at:
                user.email_verified_at = timezone.now()
            user.save(
                update_fields=[
                    "google_id",
                    "auth_provider",
                    "first_name",
                    "last_name",
                    "email_verified_at",
                ]
            )
            return build_token_response(user)
        raise AuthServiceError(
            400,
            "Un compte existe déjà avec cet email via une autre méthode de connexion.",
        )

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        auth_provider=User.AuthProvider.GOOGLE,
        google_id=google_id,
        email_verified_at=timezone.now(),
        is_status_searchable=True,
    )
    user.set_unusable_password()
    user.save()

    return build_token_response(user)


def handle_auth_error(exc: AuthServiceError):
    raise HttpError(exc.status_code, exc.message)
