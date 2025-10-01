from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Delivery, DeliveryItem


@transaction.atomic
def validate_delivery(delivery_id: int, validated_by_user, validation_data: Dict[int, Decimal]) -> Delivery:
    """Procesează validarea unui aviz.

    - Setează `quantity_accepted` pentru fiecare item
    - Marcează discrepanțele
    - Actualizează `OrderItem.quantity_delivered`
    - Setează statusurile și câmpurile de audit
    """

    delivery = Delivery.objects.select_for_update().get(pk=delivery_id)
    items = list(delivery.items.select_related("order_item"))

    if not items:
        raise ValidationError("Avizul nu conține poziții pentru validare.")

    total_discrepancies = 0
    for item in items:
        if item.pk not in validation_data:
            raise ValidationError(f"Lipsesc datele de validare pentru item {item.pk}.")
        qty_accepted = Decimal(validation_data[item.pk])
        item.quantity_accepted = qty_accepted
        # Discrepanță dacă acceptatul diferă de livrat
        item.has_discrepancy = qty_accepted != item.quantity_delivered
        if item.has_discrepancy:
            total_discrepancies += 1
        item.save(update_fields=["quantity_accepted", "has_discrepancy", "updated_at"])

        # Actualizăm cantitatea livrată pe poziția de comandă
        order_item = item.order_item
        order_item.quantity_delivered = (order_item.quantity_delivered or Decimal("0")) + qty_accepted
        order_item.save(update_fields=["quantity_delivered", "updated_at"])

    delivery.validation_status = "approved" if total_discrepancies == 0 else "partial"
    delivery.status = "validated"
    delivery.validated_by = validated_by_user
    from django.utils import timezone

    delivery.validated_at = timezone.now()
    delivery.save(update_fields=["validation_status", "status", "validated_by", "validated_at", "updated_at"])
    return delivery


def calculate_order_completion(order_id: int) -> dict:
    """Calculează gradul de completare al unei comenzi."""
    from orders.models import Order
    from django.db.models import Sum

    order = Order.objects.get(pk=order_id)
    agg = order.items.aggregate(
        total_ordered=Sum("quantity_ordered"), total_delivered=Sum("quantity_delivered")
    )
    total_ordered = agg["total_ordered"] or Decimal("0")
    total_delivered = agg["total_delivered"] or Decimal("0")
    percentage = Decimal("0")
    if total_ordered > 0:
        percentage = (total_delivered / total_ordered * 100).quantize(Decimal("0.01"))
    return {
        "total_ordered": total_ordered,
        "total_delivered": total_delivered,
        "percentage": percentage,
        "is_complete": total_delivered >= total_ordered and total_ordered > 0,
    }


