from __future__ import annotations

from django import forms

from .models import Order, OrderItem


class DateInput(forms.DateInput):
    input_type = "date"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "order_number",
            "partner",
            "delivery_date",
            "currency",
            "notes",
        ]
        widgets = {
            "delivery_date": DateInput(),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = [
            "position",
            "material_code",
            "material_description",
            "quantity_ordered",
            "unit_of_measure",
            "delivery_date",
            "net_price",
            "price_unit",
            "price_unit_order",
        ]
        widgets = {
            "delivery_date": DateInput(),
        }


