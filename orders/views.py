from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, F
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from decimal import Decimal

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from partners.models import Partner


@method_decorator(login_required(login_url="/admin/login/?next=/orders/"), name="dispatch")
class OrderListView(ListView):
    """Listă de comenzi pentru utilizatori interni.

    Permite filtrare după status, partener și dată.
    """

    template_name = "orders/order_list.html"
    paginate_by = 20
    context_object_name = "orders"

    def get_queryset(self):  # type: ignore[no-untyped-def]
        qs = (
            Order.objects.select_related("partner")
            .prefetch_related("items")
            .order_by("-order_date")
        )
        status = self.request.GET.get("status")
        partner = self.request.GET.get("partner")
        if status:
            qs = qs.filter(status=status)
        if partner:
            qs = qs.filter(partner__name__icontains=partner)
        return qs

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        # Folosim queryset-ul complet (nepaginat) pentru statistici, apoi apelăm super()
        full_qs = self.get_queryset()
        ctx = super().get_context_data(**kwargs)
        total_orders = full_qs.count()
        active_orders = full_qs.exclude(status__in=["delivered", "cancelled"]).count()
        total_value = full_qs.aggregate(total=Sum("total_value"))['total'] or 0
        ctx.update({
            "stats": {
                "total_orders": total_orders,
                "active_orders": active_orders,
                "total_value": total_value,
            }
        })
        return ctx


@method_decorator(login_required(login_url="/admin/login/"), name="dispatch")
class OrderDetailView(DetailView):
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    model = Order

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        order: Order = ctx["order"]
        deliveries = order.deliveries.all().prefetch_related("items")
        total_ordered = order.items.aggregate(s=Sum("quantity_ordered"))['s'] or 0
        total_delivered = order.items.aggregate(s=Sum("quantity_delivered"))['s'] or 0
        percentage = 0
        if total_ordered:
            percentage = round(float(total_delivered) / float(total_ordered) * 100, 2)
        ctx.update({
            "deliveries": deliveries,
            "delivery_stats": {
                "total_ordered": total_ordered,
                "total_delivered": total_delivered,
                "percentage": percentage,
                "is_complete": order.is_fully_delivered(),
            },
        })
        return ctx


class DashboardView(TemplateView):
    template_name = "core/home.html"


@method_decorator(login_required(login_url="/admin/login/"), name="dispatch")
class OrderCreateView(CreateView):
    template_name = "orders/order_create.html"
    model = Order
    form_class = OrderForm

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, can_delete=False)
        if self.request.POST:
            ctx["formset"] = OrderItemFormSet(self.request.POST)
        else:
            ctx["formset"] = OrderItemFormSet()
        return ctx

    def form_valid(self, form):  # type: ignore[no-untyped-def]
        # Asigurăm o valoare inițială pentru total_value pentru a evita încălcarea NOT NULL
        form.instance.total_value = Decimal("0")
        response = super().form_valid(form)
        OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, can_delete=False)
        formset = OrderItemFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            from django.db.models import Sum

            total = self.object.items.aggregate(s=Sum("line_total"))["s"] or 0
            self.object.total_value = total
            self.object.save(update_fields=["total_value", "updated_at"])
            return response
        else:
            self.object.delete()
            return self.render_to_response(self.get_context_data(form=form, formset=formset))


@require_GET
def order_items_api(request, order_id: int):  # type: ignore[no-untyped-def]
    """API simplu: pozițiile unei comenzi cu cantitățile rămase (pentru populare JS)."""
    # Autorizare: staff autentificat SAU partener cu sesiune validă
    is_staff = request.user.is_authenticated and request.user.is_staff
    partner_ok = False
    code = request.session.get("partner_code")
    if code:
        partner_ok = Partner.objects.filter(partner_code=code, is_active=True).exists()
    if not (is_staff or partner_ok):
        return JsonResponse({"error": "unauthorized"}, status=401)
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"items": []})
    data = []
    for oi in order.items.all():
        remaining = oi.get_remaining_quantity()
        if remaining > 0:
            data.append({
                "id": oi.id,
                "material_code": oi.material_code,
                "material_description": oi.material_description,
                "remaining": float(remaining),
            })
    return JsonResponse({"items": data})


