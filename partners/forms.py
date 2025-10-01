from __future__ import annotations

from django import forms

from .models import Partner


class PartnerLoginForm(forms.Form):
    """Formular simplu pentru autentificarea partenerilor pe baza `partner_code`."""

    partner_code = forms.CharField(label="Cod partener", max_length=20)

    def clean_partner_code(self) -> str:  # type: ignore[override]
        code = self.cleaned_data.get("partner_code", "").strip()
        partner_exists = Partner.objects.filter(partner_code=code, is_active=True).exists()
        if not partner_exists:
            raise forms.ValidationError("Cod partener invalid sau cont inactiv.")
        return code


