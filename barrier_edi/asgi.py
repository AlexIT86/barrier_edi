"""ASGI config pentru proiectul Barrier EDI."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barrier_edi.settings")

application = get_asgi_application()


