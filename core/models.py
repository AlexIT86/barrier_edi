"""Modele comune pentru aplicația Barrier EDI."""

from __future__ import annotations

from django.db import models


class BaseModel(models.Model):
    """Model abstract de bază cu câmpuri comune.

    Include:
    - created_at: data creării înregistrării
    - updated_at: data ultimei actualizări
    - is_active: flag generic pentru activ/inactiv
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


