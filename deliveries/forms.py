from __future__ import annotations

from decimal import Decimal
from typing import Any

from django import forms
from django.forms import inlineformset_factory

from .models import Delivery, DeliveryItem
from .validators import validate_delivery_quantity


class DateInput(forms.DateInput):
    input_type = "date"


class DeliveryForm(forms.ModelForm):
    """Formular pentru crearea unui aviz de către partener."""

    class Meta:
        model = Delivery
        fields = ["order", "delivery_date", "notes"]
        widgets = {
            "delivery_date": DateInput(),
            "notes": forms.Textarea(attrs={"rows": 2}),
            # Vom popula rândurile via JS fără refresh
            "order": forms.Select(attrs={"id": "id_order"}),
        }


class DeliveryItemForm(forms.ModelForm):
    class Meta:
        model = DeliveryItem
        fields = ["order_item", "quantity_delivered", "notes"]
        widgets = {
            "quantity_delivered": forms.NumberInput(attrs={"step": "0.001", "class": "form-control form-control-sm"}),
            "notes": forms.Textarea(attrs={"rows": 1}),
        }

    def clean(self) -> dict[str, Any]:  # type: ignore[override]
        cleaned = super().clean()
        order_item = cleaned.get("order_item")
        quantity_delivered = cleaned.get("quantity_delivered")
        if order_item and quantity_delivered is not None:
            validate_delivery_quantity(quantity_delivered, order_item)
        return cleaned


DeliveryItemFormSet = inlineformset_factory(
    parent_model=Delivery,
    model=DeliveryItem,
    form=DeliveryItemForm,
    fields=["order_item", "quantity_delivered", "notes"],
    extra=0,
    can_delete=False,
)


class DeliveryValidationForm(forms.Form):
    """Formular dinamic pentru validarea cantităților acceptate pe poziții."""

    def __init__(self, *args: Any, items: list[DeliveryItem], **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for item in items:
            self.fields[f"item_{item.pk}_quantity_accepted"] = forms.DecimalField(
                label=f"Acceptat - {item.order_item.material_code}",
                max_digits=10,
                decimal_places=3,
                min_value=Decimal("0"),
                required=True,
                initial=item.quantity_delivered,
            )
        self.fields["validation_notes"] = forms.CharField(
            label="Note de validare",
            required=False,
            widget=forms.Textarea(attrs={"rows": 3}),
        )


