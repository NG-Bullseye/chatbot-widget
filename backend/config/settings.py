"""
Django settings. Everything customer-specific comes from the environment
(.env locally, real env vars in production) so the codebase stays
customer-agnostic.
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG defaults to OFF. A forgotten env var in production must not turn on
# Django's error pages -- those render the whole environment (LLM_API_KEY,
# DATABASE_URL, Langfuse keys) into the browser on any 500.
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"

if DEBUG:
    SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
    ALLOWED_HOSTS = ["*"]
else:
    # No defaults in production: the shipped key is public (it is in git), so
    # falling back to it would let anyone forge sessions and CSRF tokens.
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
    ALLOWED_HOSTS = [
        h.strip() for h in os.environ["DJANGO_ALLOWED_HOSTS"].split(",") if h.strip()
    ]

# Railway terminates TLS at its proxy and forwards plain HTTP. Without this
# Django considers the request insecure, which breaks CSRF and secure cookies.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "pgvector.django",
    "apps.chat",
    "apps.knowledge",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # Serves collected static files (widget embed.js) without a separate web
    # server. Django itself does not serve static files when DEBUG=false.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

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

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get(
            "DATABASE_URL", "postgres://chatbot:chatbot@localhost:5432/chatbot"
        ),
        conn_max_age=600,
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

LANGUAGE_CODE = "de-de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# CORS: the widget runs on the customer's website, so the backend must allow
# that origin. Comma-separated list of allowed origins.
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = False

# DSGVO-Speicherbegrenzung (Art. 5 Abs. 1 lit. e): Chat-Verlaeufe werden nicht
# unbegrenzt aufbewahrt. Das Management-Command `purge_conversations` loescht
# Conversations, die laenger als diese Frist nicht mehr aktualisiert wurden
# (Messages haengen per CASCADE dran). Per Cron taeglich ausfuehren.
CONVERSATION_RETENTION_DAYS = int(
    os.environ.get("CONVERSATION_RETENTION_DAYS", "90")
)
