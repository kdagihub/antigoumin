import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def email_configured() -> bool:
    return bool(settings.EMAIL_HOST and settings.EMAIL_HOST_USER)


def send_transactional_email(
    to_email: str,
    subject: str,
    body: str,
    *,
    reply_to: str | None = None,
    from_email: str | None = None,
) -> None:
    if not to_email:
        return
    message = body.strip()
    if not email_configured() and settings.DEBUG:
        logger.info("Email (mode log) → %s : %s\n%s", to_email, subject, message)
        return
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        reply_to=[reply_to] if reply_to else None,
    )
    email.send(fail_silently=False)
    logger.info("Email envoyé vers %s : %s", to_email, subject)


def email_for_phone(phone: str) -> str:
    from core.models import User

    if not phone:
        return ""
    user = User.objects.filter(phone_number=phone, is_active=True).first()
    return user.email if user else ""


def notify_user_by_email(to_email: str, subject: str, body: str) -> None:
    try:
        send_transactional_email(to_email, subject, body)
    except Exception:
        logger.exception("Erreur lors de l'envoi email vers %s", to_email)


def notify_phone_or_user_email(phone: str, subject: str, body: str) -> None:
    notify_user_by_email(email_for_phone(phone), subject, body)
