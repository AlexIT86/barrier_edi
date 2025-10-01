"""WSGI config pentru proiectul Barrier EDI."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barrier_edi.settings")

application = get_wsgi_application()


