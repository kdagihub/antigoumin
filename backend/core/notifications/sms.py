import logging
import threading
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from core.notifications.zavu import send_sms
from core.notifications.email import send_transactional_email

logger = logging.getLogger(__name__)


def _sms_rate_limit_key(phone: str) -> str:
    return f"agm:sms:rate:{phone}"


def check_sms_rate_limit(phone: str) -> None:
    key = _sms_rate_limit_key(phone)
    count = cache.get(key, 0)
    if count >= settings.SMS_RATE_LIMIT_PER_HOUR:
        raise ValueError("Trop de SMS envoyés récemment. Réessayez plus tard.")


def increment_sms_rate_limit(phone: str) -> None:
    key = _sms_rate_limit_key(phone)
    count = cache.get(key, 0)
    cache.set(key, count + 1, timeout=3600)


def send_verification_sms(phone: str, token: str) -> None:
    verification_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/v/{token}"
    content = (
        "AntiGoumin : une déclaration de relation vous attend. "
        f"Acceptez ou refusez ici : {verification_url}"
    )
    send_sms(phone, content)


def send_transparency_request_sms(
    phone: str,
    token: str,
    requester_name: str,
    expires_at: datetime,
) -> None:
    request_url = (
        f"{settings.FRONTEND_BASE_URL.rstrip('/')}/transparence/{token}"
    )
    content = (
        f"AntiGoumin : {requester_name} vous invite à clarifier votre statut. "
        "Vous pouvez accepter, refuser, ignorer, bloquer ou signaler. "
        f"Expire le {expires_at.strftime('%d/%m/%Y %H:%M')}. {request_url}"
    )
    send_sms(phone, content)


def send_transparency_request_sms_async(
    phone: str,
    token: str,
    requester_name: str,
    expires_at: datetime,
) -> None:
    thread = threading.Thread(
        target=_send_transparency_request_sms_safe,
        args=(phone, token, requester_name, expires_at),
        daemon=True,
    )
    thread.start()


def _send_transparency_request_sms_safe(
    phone: str,
    token: str,
    requester_name: str,
    expires_at: datetime,
) -> None:
    try:
        check_sms_rate_limit(phone)
        send_transparency_request_sms(
            phone,
            token,
            requester_name,
            expires_at,
        )
        increment_sms_rate_limit(phone)
    except ValueError as exc:
        logger.warning("SMS transparence non envoyé pour %s : %s", phone, exc)
    except Exception:
        logger.exception("Erreur SMS transparence pour %s", phone)


def send_alliance_ended_sms(phone: str, ended_at: datetime) -> None:
    content = (
        "AntiGoumin : votre Alliance Digitale a pris fin le "
        f"{ended_at.strftime('%d/%m/%Y %H:%M')}. "
        "Aucun motif ni autre statut relationnel n'est communiqué."
    )
    send_sms(phone, content)


def send_alliance_ended_sms_async(phone: str, ended_at: datetime) -> None:
    thread = threading.Thread(
        target=_send_alliance_ended_sms_safe,
        args=(phone, ended_at),
        daemon=True,
    )
    thread.start()


def _send_alliance_ended_sms_safe(phone: str, ended_at: datetime) -> None:
    try:
        check_sms_rate_limit(phone)
        send_alliance_ended_sms(phone, ended_at)
        increment_sms_rate_limit(phone)
    except ValueError as exc:
        logger.warning("SMS fin d'Alliance non envoyé pour %s : %s", phone, exc)
    except Exception:
        logger.exception("Erreur SMS fin d'Alliance pour %s", phone)


def send_verification_sms_async(phone: str, token: str) -> None:
    thread = threading.Thread(
        target=_send_verification_sms_safe,
        args=(phone, token),
        daemon=True,
    )
    thread.start()


def _send_verification_sms_safe(phone: str, token: str) -> None:
    try:
        check_sms_rate_limit(phone)
        send_verification_sms(phone, token)
        increment_sms_rate_limit(phone)
    except ValueError as exc:
        logger.warning("SMS non envoyé pour %s : %s", phone, exc)
    except Exception:
        logger.exception("Erreur lors de l'envoi SMS pour %s", phone)


def notify_user_by_email(to_email: str, subject: str, body: str) -> None:
    try:
        send_transactional_email(to_email, subject, body)
    except Exception:
        logger.exception("Erreur lors de l'envoi email vers %s", to_email)
