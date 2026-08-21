import re

PHONE_DIGITS_RE = re.compile(r"\D")


def normalize_phone(value: str) -> str:
    cleaned = PHONE_DIGITS_RE.sub("", value.strip())
    if not cleaned:
        raise ValueError("Le numéro de téléphone est obligatoire.")
    if len(cleaned) < 8 or len(cleaned) > 15:
        raise ValueError("Le numéro de téléphone est invalide.")
    return cleaned


def to_e164(value: str, default_country_code: str = "225") -> str:
    """Formate un numéro pour l'API D7 (indicatif pays obligatoire)."""
    digits = normalize_phone(value)
    if digits.startswith(default_country_code):
        return f"+{digits}"
    # En Côte d'Ivoire, le 0 initial fait partie du numéro national (+225 07…).
    if len(digits) == 10:
        return f"+{default_country_code}{digits}"
    return f"+{digits}"
