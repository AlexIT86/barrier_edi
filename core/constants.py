"""Constante globale pentru aplicația Barrier EDI.

Aceste constante definesc listele de alegeri pentru statusurile comenzilor,
avizelor de livrare și validărilor.
"""

from __future__ import annotations

ORDER_STATUS_CHOICES: list[tuple[str, str]] = [
    ("pending", "În așteptare"),
    ("sent_to_partner", "Trimisă către partener"),
    ("in_delivery", "În livrare"),
    ("delivered", "Livrată"),
    ("cancelled", "Anulată"),
]

DELIVERY_STATUS_CHOICES: list[tuple[str, str]] = [
    ("draft", "Draft"),
    ("submitted", "Trimis"),
    ("validating", "În validare"),
    ("validated", "Validat"),
    ("rejected", "Respins"),
]

VALIDATION_STATUS_CHOICES: list[tuple[str, str]] = [
    ("pending", "Pending"),
    ("approved", "Aprobat"),
    ("rejected", "Respins"),
    ("partial", "Parțial"),
]


