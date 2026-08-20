import os
from urllib.parse import unquote, urlparse


def get_database_config() -> dict:
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        parsed = urlparse(database_url)
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path.lstrip("/"),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "localhost",
            "PORT": str(parsed.port or 5432),
        }

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "antigoumin"),
        "USER": os.environ.get("POSTGRES_USER", "antigoumin"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "antigoumin"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
