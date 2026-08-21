import logging

from django.conf import settings
from django.core.cache import cache
from ninja.errors import HttpError

from core.notifications.email import send_transactional_email

logger = logging.getLogger(__name__)


class ContactServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def handle_contact_error(exc: ContactServiceError):
    raise HttpError(exc.status_code, exc.message)


def _rate_key(ip: str) -> str:
    return f"agm:contact:{ip}"


def submit_contact(
    *,
    name: str,
    email: str,
    destination: str,
    message: str,
    website: str,
    ip: str,
) -> str:
    if website.strip():
        return "Votre message a bien été transmis."

    dest = destination.strip().lower()
    if dest not in {"contact", "privacy"}:
        raise ContactServiceError(400, "Destinataire invalide.")

    key = _rate_key(ip or "unknown")
    count = cache.get(key, 0)
    if count >= settings.CONTACT_RATE_LIMIT_PER_HOUR:
        raise ContactServiceError(
            429,
            "Trop de messages envoyés récemment. Réessayez plus tard.",
        )

    target = (
        settings.PRIVACY_EMAIL if dest == "privacy" else settings.CONTACT_EMAIL
    )
    try:
        send_transactional_email(
            target,
            f"[AntiGoumin] Message {dest} — {name}",
            (
                f"Nom : {name}\n"
                f"Email : {email}\n"
                f"Destinataire : {dest}\n\n"
                f"{message.strip()}"
            ),
            reply_to=email,
        )
    except Exception as exc:
        logger.exception("Envoi du message de contact vers %s impossible", target)
        raise ContactServiceError(
            502,
            (
                "L'envoi a échoué pour une raison technique. "
                f"Écrivez-nous directement à {target}."
            ),
        ) from exc
    cache.set(key, count + 1, timeout=3600)
    return (
        "Votre message a bien été transmis. "
        "Si vous n'avez pas de réponse sous 24 h, vérifiez vos courriers indésirables."
    )
