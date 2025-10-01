"""Configurări principale pentru proiectul Barrier EDI.

Acest fișier conține setările de bază pentru mediul de dezvoltare:
- încărcarea cheilor din variabile de mediu (folosind `python-decouple`)
- aplicații instalate (inclusiv DRF și Crispy Forms cu Bootstrap 5)
- motorul de template-uri cu directorul global `templates`
- baza de date SQLite
- localizare pentru România și fus orar Europe/Bucharest
- directoarele pentru fișiere statice și media

Notă: Pentru producție, recomandăm definirea unui fișier de setări separat
și dezactivarea `DEBUG`.
"""

from __future__ import annotations

from pathlib import Path
from decouple import config


# Calea de bază a proiectului
BASE_DIR = Path(__file__).resolve().parent.parent


# Securitate
SECRET_KEY = config("SECRET_KEY", default="insecure-development-key-change-me")
DEBUG = config("DEBUG", cast=bool, default=True)
ALLOWED_HOSTS: list[str] = ["*"]  # Pentru development


# Aplicații instalate
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_extensions",  # opțional în development

    # Apps locale
    "core",
    "orders",
    "partners",
    "deliveries",
]


# Middleware standard
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Rute și template-uri
ROOT_URLCONF = "barrier_edi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


WSGI_APPLICATION = "barrier_edi.wsgi.application"


# Baza de date: SQLite pentru development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Validatori parole (standard Django)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Localizare
LANGUAGE_CODE = "ro-ro"
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True


# Fișiere statice și media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Câmp implicit pentru modele
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Crispy Forms (Bootstrap 5)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# Django REST Framework - setări de bază: paginare și permisiuni
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # În funcție de nevoi, se poate schimba în IsAuthenticated / IsAdminUser
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}


# Config SAP (placeholder) – pot fi folosite de servicii
SAP_API_URL = config("SAP_API_URL", default="http://placeholder-sap-api.local/api/v1")
SAP_API_KEY = config("SAP_API_KEY", default="placeholder-api-key")
SAP_API_TIMEOUT = config("SAP_API_TIMEOUT", cast=int, default=30)

# Login redirects
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/orders/"
LOGOUT_REDIRECT_URL = "/"

# CSRF trusted origins (pentru deploy)
CSRF_TRUSTED_ORIGINS = [
    "https://barrier-edi.dot-net.app",
]


