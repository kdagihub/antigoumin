import secrets

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError

from core.models import User
from core.notifications.email import notify_user_by_email

from .schemas import VerificationMessageSchema
from .services import AuthServiceError


GENERIC_RESET_MESSAGE = (
    "Si un compte email existe avec cette adresse, "
    "un lien de réinitialisation vient d’être envoyé. "
    "Pensez à vérifier vos courriers indésirables. (Les SPAMS)"
)


def _reset_token_key(token: str) -> str:
    return f"agm:password-reset:{token}"


def _reset_user_key(user_id: int) -> str:
    return f"agm:password-reset-user:{user_id}"


def _reset_rate_key(ip: str) -> str:
    return f"agm:password-reset-rate:{ip or 'unknown'}"


def request_password_reset(email: str, *, ip: str = "") -> VerificationMessageSchema:
    key = _reset_rate_key(ip)
    count = cache.get(key, 0)
    if count >= settings.PASSWORD_RESET_RATE_LIMIT_PER_HOUR:
        raise AuthServiceError(
            429,
            "Trop de demandes récentes. Réessayez plus tard.",
        )

    normalized_email = User.objects.normalize_email(email.strip())
    user = User.objects.filter(email=normalized_email, is_active=True).first()
    if user and user.has_usable_password():
        previous = cache.get(_reset_user_key(user.id))
        if previous:
            cache.delete(_reset_token_key(previous))
        token = secrets.token_urlsafe(32)
        ttl = settings.PASSWORD_RESET_TTL_HOURS * 3600
        cache.set(_reset_token_key(token), user.id, timeout=ttl)
        cache.set(_reset_user_key(user.id), token, timeout=ttl)
        reset_url = (
            f"{settings.FRONTEND_BASE_URL.rstrip('/')}/reinitialiser-mot-de-passe/{token}"
        )
        notify_user_by_email(
            user.email,
            "Réinitialisez votre mot de passe AntiGoumin",
            (
                f"Bonjour {user.full_name or ''},\n\n"
                "Vous avez demandé à réinitialiser votre mot de passe AntiGoumin.\n"
                f"{reset_url}\n\n"
                f"Ce lien expire dans {settings.PASSWORD_RESET_TTL_HOURS} heure(s).\n"
                "Si vous n’êtes pas à l’origine de cette demande, ignorez ce message."
            ),
        )

    cache.set(key, count + 1, timeout=3600)
    return VerificationMessageSchema(message=GENERIC_RESET_MESSAGE)


def confirm_password_reset(token: str, password: str) -> VerificationMessageSchema:
    user_id = cache.get(_reset_token_key(token))
    if not user_id:
        raise AuthServiceError(400, "Lien de réinitialisation invalide ou expiré.")
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist as exc:
        raise AuthServiceError(404, "Utilisateur introuvable.") from exc
    if not user.has_usable_password():
        raise AuthServiceError(
            400,
            "Ce compte utilise une connexion sans mot de passe. Connectez-vous avec Google.",
        )
    try:
        validate_password(password, user)
    except ValidationError as exc:
        raise AuthServiceError(400, " ".join(exc.messages)) from exc
    user.set_password(password)
    user.save(update_fields=["password"])
    cache.delete(_reset_token_key(token))
    cache.delete(_reset_user_key(user.id))
    return VerificationMessageSchema(
        message="Votre mot de passe a été mis à jour. Vous pouvez vous connecter."
    )
