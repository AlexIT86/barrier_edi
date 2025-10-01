from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from partners.decorators import require_partner_login
from partners.models import Partner
from orders.models import Order, OrderItem

from .forms import DeliveryForm, DeliveryItemFormSet, DeliveryValidationForm
from .models import Delivery, DeliveryItem
from .services import validate_delivery


@method_decorator(require_partner_login, name="dispatch")
class DeliveryCreateView(CreateView):
    template_name = "deliveries/delivery_create.html"
    form_class = DeliveryForm
    model = Delivery

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = DeliveryItemFormSet(self.request.POST)
        else:
            # Populează formset-ul cu liniile rămase din comanda selectată
            initial = []
            order_id = self.request.GET.get("order")
            if order_id:
                try:
                    order = Order.objects.get(pk=int(order_id))
                    for oi in order.items.all():
                        remaining = oi.get_remaining_quantity()
                        if remaining > 0:
                            initial.append({
                                "order_item": oi.pk,
                                "quantity_delivered": remaining,
                            })
                except (Order.DoesNotExist, ValueError):
                    pass
            ctx["formset"] = DeliveryItemFormSet(initial=initial)
        return ctx

    def form_valid(self, form):  # type: ignore[no-untyped-def]
        partner: Partner = self.request.partner  # type: ignore[attr-defined]
        form.instance.partner = partner
        response = super().form_valid(form)
        # Prepopulare: dacă nu s-a trimis formset (GET sau POST fără rânduri), generăm rânduri inițiale
        formset = DeliveryItemFormSet(self.request.POST or None, instance=self.object)
        created_any = False
        if formset.is_valid() and formset.total_form_count() > 0:
            formset.save()
            created_any = True
        else:
            # Dacă nu s-au trimis poziții, populăm automat din comanda aleasă
            order: Order = form.cleaned_data["order"]
            order_items = order.items.all()
            to_create: list[DeliveryItem] = []
            for oi in order_items:
                remaining = oi.get_remaining_quantity()
                if remaining > 0:
                    to_create.append(
                        DeliveryItem(
                            delivery=self.object,
                            order_item=oi,
                            quantity_delivered=remaining,
                        )
                    )
            if to_create:
                DeliveryItem.objects.bulk_create(to_create)
                created_any = True

        from django.utils import timezone

        self.object.status = "submitted"
        self.object.submitted_at = timezone.now()
        self.object.save(update_fields=["status", "submitted_at", "updated_at"])
        if created_any:
            messages.success(self.request, "Avizul a fost trimis. Pozițiile au fost preluate din comandă.")
        else:
            messages.warning(self.request, "Aviz creat fără poziții (nu există cantități rămase).")
        return response


@method_decorator(login_required(login_url="/admin/login/"), name="dispatch")
class DeliveryListView(ListView):
    template_name = "deliveries/delivery_list.html"
    context_object_name = "deliveries"
    paginate_by = 20

    def get_queryset(self):  # type: ignore[no-untyped-def]
        qs = Delivery.objects.select_related("order", "partner").prefetch_related("items")
        status = self.request.GET.get("status")
        vstatus = self.request.GET.get("validation_status")
        partner = self.request.GET.get("partner")
        if status:
            qs = qs.filter(status=status)
        if vstatus:
            qs = qs.filter(validation_status=vstatus)
        if partner:
            qs = qs.filter(partner__name__icontains=partner)
        return qs.order_by("-delivery_date")


@method_decorator(login_required, name="dispatch")
class DeliveryValidateView(UpdateView):
    template_name = "deliveries/delivery_validate.html"
    model = Delivery
    fields: list[str] = []  # folosim formular dinamic

    def get_context_data(self, **kwargs):  # type: ignore[no-untyped-def]
        ctx = super().get_context_data(**kwargs)
        items = list(self.object.items.select_related("order_item"))  # type: ignore[union-attr]
        form = DeliveryValidationForm(items=items)
        # Preconstruim perechi (item, field) pentru a evita accesul dinamic în template
        item_fields = []
        for item in items:
            field_name = f"item_{item.pk}_quantity_accepted"
            item_fields.append((item, form[field_name]))
        ctx["form"] = form
        ctx["items"] = items
        ctx["item_fields"] = item_fields
        return ctx

    def post(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        self.object = self.get_object()
        items = list(self.object.items.select_related("order_item"))
        form = DeliveryValidationForm(request.POST, items=items)
        if form.is_valid():
            data = {}
            for item in items:
                key = f"item_{item.pk}_quantity_accepted"
                data[item.pk] = Decimal(form.cleaned_data[key])
            validate_delivery(self.object.pk, request.user, data)
            self.object.validation_notes = form.cleaned_data.get("validation_notes", "")
            self.object.save(update_fields=["validation_notes", "updated_at"])
            messages.success(request, "Aviz validat cu succes.")
            return redirect(self.object.get_absolute_url())
        messages.error(request, "Formular invalid. Te rugăm să corectezi erorile.")
        return render(request, self.template_name, {"form": form, "object": self.object, "items": items})


class DeliveryDetailView(DetailView):
    template_name = "deliveries/delivery_detail.html"
    context_object_name = "delivery"
    model = Delivery


