from __future__ import annotations

from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "position",
        "material_code",
        "material_description",
        "quantity_ordered",
        "quantity_delivered",
        "unit_of_measure",
        "net_price",
        "line_total",
    )
    readonly_fields = ("line_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "partner",
        "order_date",
        "total_value",
        "status",
    ]
    list_filter = ["status", "partner", "order_date"]
    search_fields = ["order_number", "partner__name"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "position",
        "material_code",
        "quantity_ordered",
        "quantity_delivered",
    ]


