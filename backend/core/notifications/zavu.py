import logging

import requests
from django.conf import settings

from core.utils.phone import to_e164

logger = logging.getLogger(__name__)


class ZavuSmsError(Exception):
    pass


def _zavu_configured() -> bool:
    return bool(settings.ZAVU_API_KEY and settings.ZAVU_SENDER_ID)


def send_sms(phone: str, content: str) -> None:
    if not _zavu_configured():
        logger.info("SMS (mode log, Zavu non configuré) → %s : %s", phone, content)
        return

    recipient = to_e164(phone)
    response = requests.post(
        f"{settings.ZAVU_API_BASE_URL.rstrip('/')}/v1/messages",
        json={
            "to": recipient,
            "text": content,
            "channel": "sms",
        },
        headers={
            "Authorization": f"Bearer {settings.ZAVU_API_KEY}",
            "Zavu-Sender": settings.ZAVU_SENDER_ID,
            "Content-Type": "application/json",
        },
        timeout=20,
    )
    if not response.ok:
        logger.error(
            "Échec envoi SMS Zavu vers %s : %s %s",
            recipient,
            response.status_code,
            response.text[:500],
        )
        raise ZavuSmsError(f"Envoi SMS Zavu refusé ({response.status_code}).")
    logger.info(
        "SMS Zavu envoyé vers %s (sender=%s).",
        recipient,
        settings.ZAVU_SENDER_ID,
    )
