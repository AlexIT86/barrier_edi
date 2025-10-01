"""Modele pentru avize de livrare și poziții de aviz."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse

from core.models import BaseModel
from core.constants import DELIVERY_STATUS_CHOICES, VALIDATION_STATUS_CHOICES


User = get_user_model()


def _generate_delivery_number() -> str:
    """Generează un număr de aviz de forma `AVZ-YYYYMMDD-XXXX`.

    Nota: Simplu, bazat pe numărul de obiecte create în aceeași zi.
    Pentru concurență ridicată se poate trece la o abordare cu secvențe dedicate.
    """

    today = datetime.now().strftime("%Y%m%d")
    # Contorizăm câte avize există deja în ziua curentă pentru a incrementa sufixul
    count_today = Delivery.objects.filter(
        created_at__date=datetime.now().date()
    ).count() + 1
    return f"AVZ-{today}-{count_today:04d}"


class Delivery(BaseModel):
    """Aviz de livrare creat de partener și validat intern."""

    delivery_number = models.CharField(max_length=50, unique=True)
    order = models.ForeignKey(
        "orders.Order", on_delete=models.CASCADE, related_name="deliveries"
    )
    partner = models.ForeignKey("partners.Partner", on_delete=models.CASCADE)
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default="submitted")
    validation_status = models.CharField(
        max_length=20, choices=VALIDATION_STATUS_CHOICES, default="pending"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    validation_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-delivery_date"]
        verbose_name = "Aviz livrare"
        verbose_name_plural = "Avize livrare"

    def __str__(self) -> str:  # pragma: no cover
        return self.delivery_number

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Generează automat `delivery_number` dacă nu este setat."""
        if not self.delivery_number:
            self.delivery_number = _generate_delivery_number()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("deliveries:delivery_detail", args=[self.pk])

    def get_total_items(self) -> int:
        return self.items.count()

    def has_discrepancies(self) -> bool:
        """Există diferențe între cantitățile comandate și cele livrate?"""
        return self.items.filter(has_discrepancy=True).exists()

    def calculate_discrepancies(self) -> dict[int, Decimal]:
        """Returnează un dict {item_id: diferență} pentru fiecare poziție."""
        result: dict[int, Decimal] = {}
        for item in self.items.select_related("order_item"):
            result[item.pk] = item.calculate_discrepancy()
        return result


class DeliveryItem(BaseModel):
    """Poziție dintr-un aviz de livrare."""

    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, related_name="items"
    )
    order_item = models.ForeignKey(
        "orders.OrderItem", on_delete=models.CASCADE, related_name="delivery_items"
    )
    quantity_delivered = models.DecimalField(max_digits=10, decimal_places=3)
    quantity_accepted = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    has_discrepancy = models.BooleanField(default=False)
    discrepancy_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["order_item__position"]
        verbose_name = "Poziție aviz"
        verbose_name_plural = "Poziții aviz"

    def __str__(self) -> str:  # pragma: no cover
        return f"Aviz {self.delivery.delivery_number} - {self.order_item}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Detectează automat discrepanțe înainte de salvare.

        Discrepanță atunci când `quantity_delivered` diferă de cantitatea disponibilă
        rămasă pentru `order_item`.
        """
        remaining = self.get_remaining_quantity()
        self.has_discrepancy = self.quantity_delivered != remaining
        super().save(*args, **kwargs)

    def get_ordered_quantity(self) -> Decimal:
        return self.order_item.quantity_ordered

    def get_remaining_quantity(self) -> Decimal:
        return self.order_item.get_remaining_quantity()

    def calculate_discrepancy(self) -> Decimal:
        """Diferența dintre livrat și cantitatea încă disponibilă.

        Valoare pozitivă indică surplus livrat; negativă indică mai puțin decât disponibil.
        """
        return (self.quantity_delivered - self.get_remaining_quantity()).quantize(Decimal("0.001"))


