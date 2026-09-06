import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_list(name: str, default: str = "") -> list[str]:
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def build_csrf_trusted_origins(allowed_hosts: list[str]) -> list[str]:
    origins = env_list("CSRF_TRUSTED_ORIGINS", "")
    seen = set(origins)

    # L'admin Django est servi sur le domaine API : il doit être trusted aussi.
    for host in allowed_hosts:
        if host in ("*", ""):
            continue
        for scheme in ("https", "http"):
            origin = f"{scheme}://{host}"
            if origin not in seen:
                origins.append(origin)
                seen.add(origin)

    return origins


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "*") or ["*"]
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
CSRF_TRUSTED_ORIGINS = build_csrf_trusted_origins(ALLOWED_HOSTS)
CORS_ALLOW_CREDENTIALS = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "core.apps.CoreConfig",
    "geniuspay",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

from config.database import get_database_config

DATABASES = {
    "default": get_database_config(),
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://redis:6379/1"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "core.User"

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_LIFETIME = timedelta(
    hours=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME_HOURS", "24"))
)

GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:5173")
PAYMENT_WEBHOOK_SECRET = os.environ.get("PAYMENT_WEBHOOK_SECRET", "")
GENIUSPAY_BASE_URL = os.environ.get(
    "GENIUSPAY_BASE_URL", "https://geniuspay.ci/api/v1/merchant"
)
GENIUSPAY_API_KEY = os.environ.get("GENIUSPAY_API_KEY", "")
GENIUSPAY_API_SECRET = os.environ.get("GENIUSPAY_API_SECRET", "")
GENIUSPAY_WEBHOOK_SECRET = os.environ.get("GENIUSPAY_WEBHOOK_SECRET", "")
GENIUSPAY_ENVIRONMENT = os.environ.get("GENIUSPAY_ENVIRONMENT", "sandbox")
GENIUSPAY_TIMEOUT = int(os.environ.get("GENIUSPAY_TIMEOUT", "30"))
GENIUSPAY = {
    "API_KEY": GENIUSPAY_API_KEY,
    "API_SECRET": GENIUSPAY_API_SECRET,
    "WEBHOOK_SECRET": GENIUSPAY_WEBHOOK_SECRET or None,
    "SANDBOX": GENIUSPAY_ENVIRONMENT != "live",
    "ENVIRONMENT": GENIUSPAY_ENVIRONMENT,
    "TIMEOUT": GENIUSPAY_TIMEOUT,
}

ZAVU_API_KEY = os.environ.get("ZAVU_API_KEY", "")
ZAVU_SENDER_ID = os.environ.get("ZAVU_SENDER_ID", "")
ZAVU_API_BASE_URL = os.environ.get("ZAVU_API_BASE_URL", "https://api.zavu.dev")

EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "465"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER") or os.environ.get("EMAIL_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD") or os.environ.get(
    "EMAIL_PASSWORD", ""
)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", "True" if EMAIL_PORT == 465 else "False") == "True"
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True" if EMAIL_PORT == 587 else "False") == "True"
if EMAIL_USE_SSL:
    EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER or "noreply@antigoumin.live",
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.console.EmailBackend"
)
VERIFICATION_TOKEN_TTL = timedelta(
    minutes=int(os.environ.get("VERIFICATION_TOKEN_TTL_MINUTES", "15"))
)
VERIFICATION_ACCESS_TTL_HOURS = int(os.environ.get("VERIFICATION_ACCESS_TTL_HOURS", "24"))
TRANSPARENCY_REQUEST_TTL_HOURS = int(
    os.environ.get("TRANSPARENCY_REQUEST_TTL_HOURS", "48")
)
TRANSPARENCY_REQUEST_COOLDOWN_HOURS = int(
    os.environ.get("TRANSPARENCY_REQUEST_COOLDOWN_HOURS", "168")
)
SUBSCRIPTION_DURATION_DAYS = int(os.environ.get("SUBSCRIPTION_DURATION_DAYS", "30"))
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "contact@antigoumin.live")
PRIVACY_EMAIL = os.environ.get("PRIVACY_EMAIL", "privacy@antigoumin.live")
EMAIL_VERIFICATION_TTL_HOURS = int(os.environ.get("EMAIL_VERIFICATION_TTL_HOURS", "24"))
PHONE_OTP_TTL_MINUTES = int(os.environ.get("PHONE_OTP_TTL_MINUTES", "10"))
PHONE_OTP_RESEND_COOLDOWN_SECONDS = int(
    os.environ.get("PHONE_OTP_RESEND_COOLDOWN_SECONDS", "60")
)
PHONE_OTP_MAX_ATTEMPTS = int(os.environ.get("PHONE_OTP_MAX_ATTEMPTS", "5"))
CONTACT_RATE_LIMIT_PER_HOUR = int(os.environ.get("CONTACT_RATE_LIMIT_PER_HOUR", "5"))
SMS_RATE_LIMIT_PER_HOUR = int(os.environ.get("SMS_RATE_LIMIT_PER_HOUR", "5"))
PASSWORD_RESET_TTL_HOURS = int(os.environ.get("PASSWORD_RESET_TTL_HOURS", "1"))
PASSWORD_RESET_RATE_LIMIT_PER_HOUR = int(
    os.environ.get("PASSWORD_RESET_RATE_LIMIT_PER_HOUR", "5")
)
MAX_UPLOAD_IMAGE_SIZE = int(os.environ.get("MAX_UPLOAD_IMAGE_SIZE", str(5 * 1024 * 1024)))
ALLOWED_IMAGE_CONTENT_TYPES = ("image/jpeg", "image/png", "image/webp")

from core.pricing import SERVICE_PRICES

SERVICE_PRICES = SERVICE_PRICES

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
