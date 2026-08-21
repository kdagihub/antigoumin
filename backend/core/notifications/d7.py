import logging

import requests
from django.conf import settings
from django.core.cache import cache

from core.utils.phone import to_e164

logger = logging.getLogger(__name__)

TOKEN_CACHE_KEY = "agm:d7:access_token"
TOKEN_CACHE_TTL = 50 * 60


class D7SmsError(Exception):
    pass


def _d7_configured() -> bool:
    return bool(
        settings.D7_TOKEN
        or (settings.D7_CLIENT_ID and settings.D7_CLIENT_SECRET)
    )


def _fetch_access_token() -> str:
    if settings.D7_TOKEN:
        return settings.D7_TOKEN

    cached = cache.get(TOKEN_CACHE_KEY)
    if cached:
        return cached

    response = requests.post(
        f"{settings.D7_API_BASE_URL.rstrip('/')}/auth/v1/login/application",
        json={
            "client_id": settings.D7_CLIENT_ID,
            "client_secret": settings.D7_CLIENT_SECRET,
        },
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=15,
    )
    if not response.ok:
        raise D7SmsError(
            f"Authentification D7 impossible ({response.status_code})."
        )
    payload = response.json()
    token = (
        payload.get("access_token")
        or payload.get("token")
        or payload.get("data", {}).get("access_token")
    )
    if not token:
        raise D7SmsError("Réponse D7 sans jeton d'accès.")
    cache.set(TOKEN_CACHE_KEY, token, timeout=TOKEN_CACHE_TTL)
    return token


def send_sms(phone: str, content: str) -> None:
    if not _d7_configured():
        logger.info("SMS (mode log, D7 non configuré) → %s : %s", phone, content)
        return

    recipient = to_e164(phone)
    originator = settings.D7_ORIGINATOR
    response = requests.post(
        f"{settings.D7_API_BASE_URL.rstrip('/')}/messages/v1/send",
        json={
            "messages": [
                {
                    "channel": "sms",
                    "recipients": [recipient],
                    "content": content,
                    "msg_type": "text",
                    "data_coding": "auto",
                }
            ],
            "message_globals": {
                "originator": originator,
            },
        },
        headers={
            "Authorization": f"Bearer {_fetch_access_token()}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=20,
    )
    if not response.ok:
        logger.error(
            "Échec envoi SMS D7 vers %s : %s %s",
            recipient,
            response.status_code,
            response.text[:500],
        )
        raise D7SmsError(f"Envoi SMS D7 refusé ({response.status_code}).")
    logger.info("SMS D7 envoyé vers %s (originator=%s).", recipient, originator)
