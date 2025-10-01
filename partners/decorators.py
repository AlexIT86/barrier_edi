from __future__ import annotations

from functools import wraps
from typing import Callable

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import Partner


def require_partner_login(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """Decorator care asigură autentificarea partenerului prin sesiune.

    Verifică existența cheii `partner_code` în sesiune, validează partenerul și
    atașează obiectul `request.partner` pentru acces ușor în view-uri.
    """

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:  # type: ignore[no-untyped-def]
        partner_code = request.session.get("partner_code")
        if not partner_code:
            messages.warning(request, "Te rugăm să te autentifici ca partener.")
            return redirect("core:home")

        partner = Partner.objects.filter(partner_code=partner_code).first()
        if not partner or not partner.is_active:
            request.session.pop("partner_code", None)
            messages.error(request, "Contul de partener nu este activ sau nu există.")
            return redirect("core:home")

        # Atașăm partenerul la request pentru utilizare ulterioară
        request.partner = partner  # type: ignore[attr-defined]
        return view_func(request, *args, **kwargs)

    return _wrapped_view


