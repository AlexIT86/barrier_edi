from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Order, OrderItem


@transaction.atomic
def import_sap_order(sap_order_data: Dict[str, Any]) -> Order:
    """Importă o comandă dintr-un dict în format SAP simplificat.

    Așteaptă chei: order_number, partner, order_date, delivery_date, currency,
    total_value (opțional, recalculat), items: list[dict].
    """

    required_top = [
        "order_number",
        "partner_code",
        "order_date",
        "delivery_date",
        "currency",
        "items",
    ]
    for key in required_top:
        if key not in sap_order_data:
            raise ValidationError(f"Câmp lipsă în comandă: {key}")

    partner_code = sap_order_data["partner_code"]
    from partners.models import Partner

    partner = Partner.objects.filter(partner_code=partner_code).first()
    if not partner:
        raise ValidationError(f"Partener inexistent: {partner_code}")

    order, _created = Order.objects.update_or_create(
        order_number=sap_order_data["order_number"],
        defaults={
            "partner": partner,
            "order_date": sap_order_data["order_date"],
            "delivery_date": sap_order_data["delivery_date"],
            "currency": sap_order_data.get("currency", "RON"),
            "status": "pending",
            "notes": sap_order_data.get("notes", ""),
            "total_value": Decimal("0"),
        },
    )

    # Curățăm pozițiile existente și le recreăm din datele SAP
    order.items.all().delete()
    total_value = Decimal("0")
    for item in sap_order_data["items"]:
        required_item = [
            "position",
            "material_code",
            "material_description",
            "quantity_ordered",
            "unit_of_measure",
            "delivery_date",
            "net_price",
            "price_unit",
        ]
        for key in required_item:
            if key not in item:
                raise ValidationError(f"Câmp lipsă în poziție: {key}")

        oi = OrderItem.objects.create(
            order=order,
            position=item["position"],
            material_code=item["material_code"],
            material_description=item["material_description"],
            quantity_ordered=Decimal(str(item["quantity_ordered"])),
            unit_of_measure=item["unit_of_measure"],
            delivery_date=item["delivery_date"],
            net_price=Decimal(str(item["net_price"])),
            price_unit=item["price_unit"],
            price_unit_order=item.get("price_unit_order", ""),
            line_total=Decimal("0"),
        )
        total_value += oi.line_total

    order.total_value = total_value
    order.save(update_fields=["total_value", "updated_at"])
    return order


def sync_sap_orders(file_path: str | None = None, dry_run: bool = False) -> dict:
    """Simulează sincronizarea comenzilor din SAP.

    - Dacă `file_path` este furnizat, citește JSON local
    - Altfel, construiește date mock
    - Pentru fiecare comandă: apelează `import_sap_order`
    """
    import json
    from datetime import date

    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # Mock data simplu
        data = [
            {
                "order_number": "CMD-1001",
                "partner_code": "PART-001",
                "order_date": date.today().isoformat(),
                "delivery_date": date.today().isoformat(),
                "currency": "RON",
                "items": [
                    {
                        "position": 10,
                        "material_code": "MAT-01",
                        "material_description": "Material test",
                        "quantity_ordered": "10.000",
                        "unit_of_measure": "BUC",
                        "delivery_date": date.today().isoformat(),
                        "net_price": "100.00",
                        "price_unit": "BUC",
                    }
                ],
            }
        ]

    results = {"success": 0, "errors": []}
    for entry in data:
        try:
            if not dry_run:
                import_sap_order(entry)
            results["success"] += 1
        except Exception as exc:  # pragma: no cover - doar logging simplu
            results["errors"].append(str(exc))
    return results


