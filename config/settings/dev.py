from datetime import timedelta
from .base import *  # noqa: F401, F403
from .base import BASE_DIR, env  # noqa: F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="django-insecure-secret-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["*"])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

FRONTEND_URL = "https://localhost.com:3000"
DEFAULT_FROM_EMAIL = "noreply@your-domain.com"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

AUTHENTICATION_BACKENDS = [
    "auth_system.authentication.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "auth_system.authentication.CookieJWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

AUTH_SYSTEM = {
    # JWT
    "JWT_ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "JWT_REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "JWT_ACCESS_COOKIE_NAME": "access_token",
    "JWT_REFRESH_COOKIE_NAME": "refresh_token",
    "JWT_COOKIE_SECURE": True,  # set False for local dev over HTTP
    "JWT_COOKIE_SAMESITE": "Lax",
    "JWT_COOKIE_HTTPONLY": True,
    # Redis
    "REDIS_URL": "redis://127.0.0.1:6379/0",
    "PENDING_SESSION_TTL": 300,  # seconds (2FA handoff window)
    "PENDING_SESSION_PREFIX": "auth:pending:",
    "PENDING_EMAIL_TTL": 3600,  # seconds (email change window)
    # 2FA
    "TOTP_ISSUER_NAME": "AuthSystem",
    "BACKUP_CODES_COUNT": 10,
    # Session
    "UPDATE_SESSION_AUTH_HASH": False,  # set True for session-based auth clients
    # Rate limiting — set None to disable
    "LOGIN_THROTTLE_RATES": {
        "login": "10/min",
        "signup": "5/min",
        "password_reset": "5/min",
        "verify_2fa": "10/min",
    },
}
