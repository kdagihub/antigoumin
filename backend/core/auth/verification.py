import secrets

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from core.models import User
from core.notifications.d7 import send_sms
from core.notifications.email import notify_user_by_email
from core.utils.phone import normalize_phone

from .schemas import VerificationMessageSchema
from .services import AuthServiceError, user_to_schema


def _email_token_key(token: str) -> str:
    return f"agm:account-email:{token}"


def _email_user_key(user_id: int) -> str:
    return f"agm:account-email-user:{user_id}"


def _otp_key(user_id: int) -> str:
    return f"agm:account-otp:{user_id}"


def _otp_cooldown_key(user_id: int) -> str:
    return f"agm:account-otp-cd:{user_id}"


def send_email_verification(user: User) -> None:
    previous = cache.get(_email_user_key(user.id))
    if previous:
        cache.delete(_email_token_key(previous))
    token = secrets.token_urlsafe(32)
    ttl = settings.EMAIL_VERIFICATION_TTL_HOURS * 3600
    cache.set(_email_token_key(token), user.id, timeout=ttl)
    cache.set(_email_user_key(user.id), token, timeout=ttl)
    verify_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/verifier-email/{token}"
    notify_user_by_email(
        user.email,
        "Confirmez votre adresse email AntiGoumin",
        (
            f"Bonjour {user.full_name or ''},\n\n"
            "Confirmez votre adresse email pour utiliser AntiGoumin :\n"
            f"{verify_url}\n\n"
            f"Ce lien expire dans {settings.EMAIL_VERIFICATION_TTL_HOURS} heures."
        ),
    )


def confirm_email_token(token: str):
    user_id = cache.get(_email_token_key(token))
    if not user_id:
        raise AuthServiceError(400, "Lien de vérification invalide ou expiré.")
    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist as exc:
        raise AuthServiceError(404, "Utilisateur introuvable.") from exc
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])
    cache.delete(_email_token_key(token))
    cache.delete(_email_user_key(user.id))
    return user_to_schema(user)


def resend_email_verification(user: User) -> VerificationMessageSchema:
    if user.email_verified:
        return VerificationMessageSchema(message="Votre email est déjà vérifié.")
    send_email_verification(user)
    return VerificationMessageSchema(
        message=(
            "Un nouveau lien de confirmation a été envoyé. "
            "Pensez à vérifier vos courriers indésirables."
        )
    )


def _assert_phone_available(phone: str, user_id: int) -> None:
    taken = (
        User.objects.filter(phone_number=phone, is_active=True)
        .exclude(id=user_id)
        .exists()
    )
    if taken:
        raise AuthServiceError(400, "Un compte utilise déjà ce numéro.")


def set_user_phone(user: User, phone_number: str):
    try:
        normalized = normalize_phone(phone_number)
    except ValueError as exc:
        raise AuthServiceError(400, str(exc)) from exc
    _assert_phone_available(normalized, user.id)
    if user.phone_number != normalized:
        user.phone_number = normalized
        user.phone_verified_at = None
        user.save(update_fields=["phone_number", "phone_verified_at"])
    return user


def send_phone_otp(user: User) -> VerificationMessageSchema:
    if not user.phone_number:
        raise AuthServiceError(400, "Ajoutez d'abord un numéro de téléphone.")
    if cache.get(_otp_cooldown_key(user.id)):
        raise AuthServiceError(
            429,
            "Un code a déjà été envoyé. Réessayez dans une minute.",
        )
    code = f"{secrets.randbelow(1_000_000):06d}"
    cache.set(
        _otp_key(user.id),
        {"code": code, "attempts": 0},
        timeout=settings.PHONE_OTP_TTL_MINUTES * 60,
    )
    cache.set(
        _otp_cooldown_key(user.id),
        True,
        timeout=settings.PHONE_OTP_RESEND_COOLDOWN_SECONDS,
    )
    send_sms(
        user.phone_number,
        f"AntiGoumin : votre code de vérification est {code}. "
        f"Il expire dans {settings.PHONE_OTP_TTL_MINUTES} minutes.",
    )
    notify_user_by_email(
        user.email,
        "Votre code de vérification téléphone AntiGoumin",
        (
            f"Un code SMS a été envoyé au {user.phone_number}.\n"
            f"Code : {code}\n"
            f"Il expire dans {settings.PHONE_OTP_TTL_MINUTES} minutes."
        ),
    )
    return VerificationMessageSchema(
        message="Un code a été envoyé par SMS. Une copie a aussi été envoyée par email."
    )


def verify_phone_otp(user: User, code: str):
    payload = cache.get(_otp_key(user.id))
    if not payload:
        raise AuthServiceError(400, "Aucun code en cours. Demandez un nouveau SMS.")
    attempts = int(payload.get("attempts", 0)) + 1
    expected = str(payload.get("code", ""))
    submitted = "".join(ch for ch in code if ch.isdigit())
    if submitted != expected:
        if attempts >= settings.PHONE_OTP_MAX_ATTEMPTS:
            cache.delete(_otp_key(user.id))
            raise AuthServiceError(
                400,
                "Trop de tentatives. Demandez un nouveau code.",
            )
        payload["attempts"] = attempts
        cache.set(
            _otp_key(user.id),
            payload,
            timeout=settings.PHONE_OTP_TTL_MINUTES * 60,
        )
        raise AuthServiceError(400, "Code incorrect.")
    if not user.phone_number:
        raise AuthServiceError(400, "Aucun numéro à vérifier.")
    user.phone_verified_at = timezone.now()
    user.save(update_fields=["phone_verified_at"])
    cache.delete(_otp_key(user.id))
    cache.delete(_otp_cooldown_key(user.id))
    return user_to_schema(user)
