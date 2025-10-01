from __future__ import annotations

from django.contrib import admin

from .models import Delivery, DeliveryItem


class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 0
    fields = (
        "order_item",
        "quantity_delivered",
        "quantity_accepted",
        "has_discrepancy",
    )
    readonly_fields = ("has_discrepancy",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        "delivery_number",
        "order",
        "partner",
        "delivery_date",
        "status",
        "validation_status",
    ]
    list_filter = ["status", "validation_status", "delivery_date"]
    search_fields = ["delivery_number", "order__order_number"]
    inlines = [DeliveryItemInline]


@admin.register(DeliveryItem)
class DeliveryItemAdmin(admin.ModelAdmin):
    list_display = [
        "delivery",
        "order_item",
        "quantity_delivered",
        "quantity_accepted",
        "has_discrepancy",
    ]


