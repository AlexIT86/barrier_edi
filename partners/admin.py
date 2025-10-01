from __future__ import annotations

from django.contrib import admin

from .models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ["partner_code", "name", "email", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["partner_code", "name", "email"]

    @admin.action(description="Activează partenerii selectați")
    def activate_partners(self, request, queryset):  # type: ignore[no-untyped-def]
        queryset.update(is_active=True)

    @admin.action(description="Dezactivează partenerii selectați")
    def deactivate_partners(self, request, queryset):  # type: ignore[no-untyped-def]
        queryset.update(is_active=False)


