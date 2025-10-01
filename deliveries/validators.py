from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from django.core.exceptions import ValidationError

from orders.models import OrderItem


def validate_delivery_quantity(quantity_delivered: Decimal, order_item: OrderItem) -> None:
    """Validează cantitatea livrată pentru un `order_item`.

    - Cantitatea trebuie să fie > 0
    - Cantitatea nu poate depăși cantitatea rămasă de livrat
    """
    if quantity_delivered is None:
        raise ValidationError("Cantitatea livrată este obligatorie.")
    if quantity_delivered <= 0:
        raise ValidationError("Cantitatea livrată trebuie să fie mai mare ca 0.")
    remaining = order_item.get_remaining_quantity()
    if quantity_delivered > remaining:
        raise ValidationError(
            f"Cantitatea livrată ({quantity_delivered}) depășește cantitatea rămasă ({remaining})."
        )


def validate_delivery_items(delivery_items_data: Iterable[dict]) -> bool:
    """Validează că toate item-urile aparțin aceleiași comenzi și nu sunt duplicate.

    Așteaptă o colecție de dict-uri cu minim cheile: `order_item`.
    """
    order_ids: set[int] = set()
    seen_items: set[int] = set()
    for data in delivery_items_data:
        item: OrderItem = data["order_item"]
        if item.pk in seen_items:
            raise ValidationError("Există item-uri duplicate în aviz.")
        seen_items.add(item.pk)
        order_ids.add(item.order_id)

    if len(order_ids) > 1:
        raise ValidationError("Toate pozițiile trebuie să aparțină aceleiași comenzi.")

    return True


