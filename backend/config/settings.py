"""Django settings for the Tabllet backend.

Configuration is driven by environment variables (see .env.example) so the same
image can run in both development and production via docker compose.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

# Read a .env file if present (mainly for local, non-docker runs).
env_file = BASE_DIR / ".env"
if env_file.exists():
    env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "api",
]

REST_FRAMEWORK = {
    # Unified {success, data, error} envelope for every response.
    "DEFAULT_RENDERER_CLASSES": [
        "api.responses.EnvelopeJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "EXCEPTION_HANDLER": "api.responses.envelope_exception_handler",
    # Token auth for the SPA/desktop client (persistent token = "자동 로그인").
    # SessionAuthentication is kept so the browsable API / admin still work.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Endpoints require auth by default; auth (register/login) opts out explicitly.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # CorsMiddleware must come before CommonMiddleware so CORS headers are added
    # even on responses CommonMiddleware short-circuits (e.g. redirects).
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="tabllet"),
        "USER": env("POSTGRES_USER", default="tabllet"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="tabllet"),
        "HOST": env("POSTGRES_HOST", default="db"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS (django-cors-headers) ---
# The frontend is a separate-origin SvelteKit/Electron client, so the browser
# needs CORS headers to call this API. In DEBUG we allow all origins for dev
# convenience (Vite dev server, file:// desktop shell); in production set
# CORS_ALLOWED_ORIGINS to the exact origins and keep allow-all off.
# An empty/unset value falls back to DEBUG (django-environ would otherwise read
# an empty string as False and defeat the dev-convenience default).
_cors_allow_all = env.str("CORS_ALLOW_ALL_ORIGINS", default="").strip().lower()
CORS_ALLOW_ALL_ORIGINS = (
    _cors_allow_all in {"1", "true", "yes", "on"} if _cors_allow_all else DEBUG
)
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:4173",  # vite preview
        "http://127.0.0.1:4173",
    ],
)
# The demo flow is unauthenticated (no session cookie), so credentials are not
# required. Leave off unless real cookie/session auth is wired up.
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=False)

# --- External services (OCR / LLM refinement / HIRA drug permit API) ---
# OCR server: receives a prescription image, returns recognized drug names.
OCR_SERVER_URL = env("OCR_SERVER_URL", default="")
# LLM refinement server: turns raw HIRA precaution text into structured JSON.
LLM_SERVER_URL = env("LLM_SERVER_URL", default="")
# data.go.kr DrugPrdtPrmsnInfoService (HIRA/MFDS) service key + endpoint.
HIRA_API_KEY = env("HIRA_API_KEY", default="")
HIRA_BASE_URL = env(
    "HIRA_BASE_URL",
    default="https://apis.data.go.kr/1471000/DrugPrdtPrmsnInfoService07/getDrugPrdtPrmsnDtlInq06",
)
# Local cache of HIRA responses (seeded from reference/hira_res.json).
HIRA_CACHE_PATH = env("HIRA_CACHE_PATH", default=str(BASE_DIR / "data" / "hira_res.json"))
# Timeout (seconds) for outbound calls to the OCR/LLM/HIRA services.
EXTERNAL_HTTP_TIMEOUT = env.float("EXTERNAL_HTTP_TIMEOUT", default=30.0)
