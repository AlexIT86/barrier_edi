"""Modele pentru gestionarea comenzilor SAP."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import models
from django.urls import reverse

from core.models import BaseModel
from core.constants import ORDER_STATUS_CHOICES


class Order(BaseModel):
    """Reprezintă o comandă SAP importată în sistem.

    Conține informații generale despre comandă și legătura cu partenerul.
    """

    order_number = models.CharField(max_length=50, unique=True)
    partner = models.ForeignKey(
        "partners.Partner", on_delete=models.CASCADE, related_name="orders"
    )
    order_date = models.DateField(auto_now_add=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="RON")
    status = models.CharField(max_length=32, choices=ORDER_STATUS_CHOICES, default="pending")
    delivery_date = models.DateField()
    sap_sync_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-order_date"]
        verbose_name = "Comandă"
        verbose_name_plural = "Comenzi"

    def __str__(self) -> str:  # pragma: no cover - reprezentare simplă
        return self.order_number

    def get_absolute_url(self) -> str:
        return reverse("orders:order_detail", args=[self.pk])

    def get_total_items(self) -> int:
        """Returnează numărul total de poziții ale comenzii."""
        return self.items.count()

    def is_fully_delivered(self) -> bool:
        """Verifică dacă toate pozițiile au fost livrate integral."""
        return not self.items.exclude(quantity_delivered__gte=models.F("quantity_ordered")).exists()


class OrderItem(BaseModel):
    """Poziție de comandă (material, cantitate, preț)."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    position = models.IntegerField()
    material_code = models.CharField(max_length=100)
    material_description = models.CharField(max_length=255)
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=3)
    unit_of_measure = models.CharField(max_length=10)
    delivery_date = models.DateField()
    net_price = models.DecimalField(max_digits=15, decimal_places=2)
    price_unit = models.CharField(max_length=10)
    price_unit_order = models.CharField(max_length=10, blank=True)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    quantity_delivered = models.DecimalField(
        default=Decimal("0"), max_digits=10, decimal_places=3
    )

    class Meta:
        ordering = ["position"]
        unique_together = [["order", "position"]]
        verbose_name = "Poziție comandă"
        verbose_name_plural = "Poziții comandă"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.order.order_number} - Poz {self.position}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Calculează automat totalul liniei înainte de salvare.

        Folosește conversie explicită la Decimal pentru a gestiona cazurile în
        care valorile sunt furnizate ca string (de ex. importuri din SAP/mock).
        """
        try:
            quantity = Decimal(str(self.quantity_ordered)) if self.quantity_ordered is not None else Decimal("0")
        except Exception:
            quantity = Decimal("0")
        try:
            price = Decimal(str(self.net_price)) if self.net_price is not None else Decimal("0")
        except Exception:
            price = Decimal("0")
        self.line_total = (quantity * price).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def get_remaining_quantity(self) -> Decimal:
        """Cantitatea rămasă de livrat pentru această poziție."""
        return (self.quantity_ordered - (self.quantity_delivered or Decimal("0"))).quantize(
            Decimal("0.001")
        )

    def is_fully_delivered(self) -> bool:
        """Verifică dacă poziția a fost livrată integral."""
        return (self.quantity_delivered or Decimal("0")) >= (self.quantity_ordered or Decimal("0"))


