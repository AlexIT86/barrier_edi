"""URL-urile principale pentru proiectul Barrier EDI.

Include rutele aplicațiilor interne și portalului parteneri.
Servește fișierele media/statice în mediul de dezvoltare.
"""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("orders/", include("orders.urls")),
    path("partners/", include("partners.urls")),
    path("deliveries/", include("deliveries.urls")),
]


if settings.DEBUG:
    # Servire fișiere media în development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Servire fișiere statice din STATICFILES_DIRS în DEBUG
    urlpatterns += staticfiles_urlpatterns()


