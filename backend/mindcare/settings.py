"""
Django settings for MindCare backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "mindcare-dev-secret-do-not-use-in-prod-2024")
DEBUG      = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mindcare.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS":    [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "mindcare.wsgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
# Defaults to SQLite (zero-setup). Switch to Mongo by installing djongo and
# setting DB_ENGINE=djongo + MONGO_URI in .env.

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

if DB_ENGINE == "djongo":
    DATABASES = {
        "default": {
            "ENGINE": "djongo",
            "NAME": os.getenv("MONGO_DB_NAME", "mindcare"),
            "CLIENT": {
                "host": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES":   ["rest_framework.parsers.JSONParser"],
}

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True            # Tighten in production
CORS_ALLOW_CREDENTIALS = True

# ── Static Files ──────────────────────────────────────────────────────────────
STATIC_URL = "/static/"

# ── ML / Gemini Config ────────────────────────────────────────────────────────
MODELS_DIR    = str(Path(__file__).resolve().parent.parent.parent / "models")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
