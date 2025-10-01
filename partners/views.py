from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.db import models
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView

from .decorators import require_partner_login
from .forms import PartnerLoginForm
from .models import Partner
from orders.models import Order


class PartnerLoginView(View):
    """Autentificare partener pe baza `partner_code` prin sesiune."""

    template_name = "partners/login.html"

    def get(self, request):  # type: ignore[no-untyped-def]
        return render(request, self.template_name, {"form": PartnerLoginForm()})

    def post(self, request):  # type: ignore[no-untyped-def]
        form = PartnerLoginForm(request.POST)
        if form.is_valid():
            partner_code = form.cleaned_data["partner_code"]
            partner = Partner.objects.get(partner_code=partner_code)
            request.session["partner_code"] = partner.partner_code
            partner.login_attempts = 0
            partner.save(update_fields=["login_attempts"])
            messages.success(request, "Autentificare reușită.")
            return redirect("partners:dashboard")

        # crește numărul de încercări dacă există un cod introdus
        code_input = request.POST.get("partner_code")
        if code_input:
            Partner.objects.filter(partner_code=code_input).update(
                login_attempts=models.F("login_attempts") + 1  # type: ignore[name-defined]
            )
        messages.error(request, "Autentificare eșuată. Verifică codul de partener.")
        return render(request, self.template_name, {"form": form})


class PartnerLogoutView(View):
    """Logout pentru partener: elimină `partner_code` din sesiune."""

    def post(self, request):  # type: ignore[no-untyped-def]
        request.session.pop("partner_code", None)
        messages.info(request, "Te-ai delogat cu succes.")
        return redirect("partners:login")

    def get(self, request):  # type: ignore[no-untyped-def]
        return self.post(request)


@method_decorator(require_partner_login, name="dispatch")
class PartnerDashboardView(TemplateView):
    template_name = "partners/dashboard.html"

    # dispatch protejat prin method_decorator mai sus

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        partner: Partner = self.request.partner  # type: ignore[attr-defined]
        active_orders = partner.get_active_orders().select_related("partner").prefetch_related("items")
        # Calculăm avizele în așteptare pentru partener, evitând importuri circulare
        try:
            from deliveries.models import Delivery  # import local

            pending_deliveries = Delivery.objects.filter(partner=partner, status="submitted").count()
        except Exception:
            pending_deliveries = 0

        ctx.update({
            "partner": partner,
            "active_orders": active_orders[:5],
            "stats": {
                "active_orders": active_orders.count(),
                "total_orders": partner.get_total_orders(),
                "pending_deliveries": pending_deliveries,
            },
        })
        return ctx


@method_decorator(require_partner_login, name="dispatch")
class PartnerOrderListView(ListView):
    template_name = "partners/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    # dispatch protejat prin method_decorator mai sus

    def get_queryset(self):  # type: ignore[no-untyped-def]
        partner: Partner = self.request.partner  # type: ignore[attr-defined]
        qs = Order.objects.filter(partner=partner).select_related("partner").prefetch_related("items")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-order_date")


@method_decorator(require_partner_login, name="dispatch")
class PartnerOrderDetailView(DetailView):
    template_name = "partners/order_detail.html"
    context_object_name = "order"
    model = Order

    # dispatch protejat prin method_decorator mai sus

    def get_object(self, queryset=None):  # type: ignore[no-untyped-def]
        obj: Order = super().get_object(queryset)
        partner: Partner = self.request.partner  # type: ignore[attr-defined]
        if obj.partner_id != partner.id:
            messages.error(self.request, "Nu ai acces la această comandă.")
            raise PermissionError("Order not owned by partner")
        return obj


@method_decorator(require_partner_login, name="dispatch")
class PartnerProfileView(TemplateView):
    template_name = "partners/profile.html"

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        ctx["partner"] = self.request.partner  # type: ignore[attr-defined]
        return ctx

    def post(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        partner: Partner = request.partner  # type: ignore[attr-defined]
        partner.name = request.POST.get("name", partner.name)
        partner.email = request.POST.get("email", partner.email)
        partner.phone = request.POST.get("phone", partner.phone)
        partner.address = request.POST.get("address", partner.address)
        partner.contact_person = request.POST.get("contact_person", partner.contact_person)
        partner.save()
        messages.success(request, "Profil actualizat.")
        return redirect("partners:profile")


def _is_staff(user):  # type: ignore[no-untyped-def]
    return user.is_authenticated and user.is_staff


@user_passes_test(_is_staff)
def partners_admin(request):  # type: ignore[no-untyped-def]
    """Pagină de administrare parteneri: listare, creare, regenerare cod."""
    from .models import Partner

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            if not name:
                messages.error(request, "Numele partenerului este obligatoriu.")
            else:
                code = Partner.generate_partner_code()
                while Partner.objects.filter(partner_code=code).exists():
                    code = Partner.generate_partner_code()
                Partner.objects.create(partner_code=code, name=name, email=email)
                messages.success(request, f"Partener creat: {code}")
            return redirect("partners:admin_page")

        if action == "regenerate" and request.POST.get("partner_id"):
            try:
                p = Partner.objects.get(pk=int(request.POST["partner_id"]))
                p.regenerate_partner_code()
                messages.success(request, f"Cod regenerat: {p.partner_code}")
            except Partner.DoesNotExist:
                messages.error(request, "Partener inexistent.")
            return redirect("partners:admin_page")

    partners_qs = Partner.objects.order_by("name")
    return render(
        request,
        "partners/admin.html",
        {"partners": partners_qs},
    )

