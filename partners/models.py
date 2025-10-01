"""Modelul pentru parteneri externi."""

from __future__ import annotations

from django.db import models
from django.urls import reverse
import secrets

from core.models import BaseModel


class Partner(BaseModel):
    """Reprezintă un partener extern conectat prin EDI.

    Autentificarea în portal se face pe baza `partner_code`.
    """

    partner_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)

    class Meta:
        ordering = ["name"]
        verbose_name = "Partener"
        verbose_name_plural = "Parteneri"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.partner_code} - {self.name}"

    @staticmethod
    def generate_partner_code(prefix: str = "PART") -> str:
        """Generează un cod unic de partener de forma `PART-XXXXXX`.

        Folosește `secrets` pentru entropie suficientă în producție.
        """
        return f"{prefix}-{secrets.token_hex(3).upper()}"

    def regenerate_partner_code(self) -> None:
        """Generează și setează un nou `partner_code` unic."""
        new_code = self.generate_partner_code()
        # ne asigurăm că este unic
        while Partner.objects.filter(partner_code=new_code).exists():
            new_code = self.generate_partner_code()
        self.partner_code = new_code
        self.save(update_fields=["partner_code", "updated_at"])

    def get_active_orders(self):
        """Returnează queryset cu comenzile active pentru acest partener."""
        from core.constants import ORDER_STATUS_CHOICES  # import local pentru a evita cicluri
        active_statuses = {"pending", "sent_to_partner", "in_delivery"}
        return self.orders.filter(status__in=active_statuses)

    def get_total_orders(self) -> int:
        """Numărul total de comenzi asociate partenerului."""
        return self.orders.count()

    def reset_login_attempts(self) -> None:
        """Resetează contorul de încercări de autentificare."""
        self.login_attempts = 0
        self.save(update_fields=["login_attempts"])


