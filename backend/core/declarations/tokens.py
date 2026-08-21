import secrets

from django.conf import settings
from django.core.cache import cache


def _verification_cache_key(token: str) -> str:
    return f"agm:verify:{token}"


def store_verification_token(declaration_id: int) -> str:
    token = secrets.token_urlsafe(32)
    cache.set(
        _verification_cache_key(token),
        declaration_id,
        timeout=int(settings.VERIFICATION_TOKEN_TTL.total_seconds()),
    )
    return token


def get_declaration_id_from_token(token: str) -> int | None:
    value = cache.get(_verification_cache_key(token))
    if value is None:
        return None
    return int(value)


def delete_verification_token(token: str) -> None:
    cache.delete(_verification_cache_key(token))
