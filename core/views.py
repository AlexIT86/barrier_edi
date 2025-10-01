from __future__ import annotations

from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.conf import settings
from django.contrib import messages


class HomeView(TemplateView):
    """Pagina principală a aplicației Barrier EDI.

    Afișează o introducere și rute rapide către zonele principale.
    """

    template_name = "core/home.html"


class StaffLoginView(View):
    """Login custom pentru utilizatori interni (staff).

    Folosește sistemul de autentificare Django sub un UI custom.
    """

    template_name = "core/staff_login.html"

    def get(self, request):  # type: ignore[no-untyped-def]
        if request.user.is_authenticated:
            return redirect("orders:order_list")
        return render(request, self.template_name)

    def post(self, request):  # type: ignore[no-untyped-def]
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Credentiale invalide.")
            return render(request, self.template_name, {"username": username})
        if not user.is_staff:
            messages.error(request, "Contul nu are drepturi de staff.")
            return render(request, self.template_name, {"username": username})
        login(request, user)
        return redirect("orders:order_list")


class StaffPasswordResetView(View):
    """Reset parolă pentru staff (mod dezvoltare sau cu token de siguranță).

    Pentru a evita e-mailul în dev, protejăm acțiunea printr-un token configurat
    în mediul de execuție: ADMIN_RESET_TOKEN (default: 'devreset').
    """

    template_name = "core/staff_reset.html"

    def get(self, request):  # type: ignore[no-untyped-def]
        return render(request, self.template_name)

    def post(self, request):  # type: ignore[no-untyped-def]
        token = request.POST.get("token", "")
        expected = getattr(settings, "ADMIN_RESET_TOKEN", "devreset")
        if token != expected:
            messages.error(request, "Token invalid.")
            return render(request, self.template_name)

        username = request.POST.get("username", "").strip()
        new_password = request.POST.get("password", "")
        if not username or not new_password:
            messages.error(request, "Completează utilizator și noua parolă.")
            return render(request, self.template_name, {"username": username})
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Utilizator inexistent.")
            return render(request, self.template_name)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        messages.success(request, "Parola a fost resetată.")
        return redirect("core:staff_login")


class StaffProfileView(View):
    """Profil simplu pentru utilizatorii staff (editare nume și email)."""

    template_name = "core/staff_profile.html"

    def get(self, request):  # type: ignore[no-untyped-def]
        if not request.user.is_authenticated:
            return redirect("core:staff_login")
        return render(request, self.template_name)

    def post(self, request):  # type: ignore[no-untyped-def]
        if not request.user.is_authenticated:
            return redirect("core:staff_login")
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save(update_fields=["first_name", "last_name", "email"])
        messages.success(request, "Profil actualizat.")
        return redirect("core:staff_profile")


def staff_logout(request):  # type: ignore[no-untyped-def]
    """Logout pentru utilizatorii staff din UI-ul custom."""
    logout(request)
    return redirect("core:home")


