from __future__ import annotations

from typing import Any

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpRequest
import json

from .services import import_sap_order


def _authorized(request: HttpRequest) -> bool:
    expected = getattr(settings, "SAP_API_KEY", None)
    provided = request.headers.get("X-API-KEY") or request.headers.get("Authorization")
    return bool(expected) and (provided == expected or provided == f"Bearer {expected}")


@csrf_exempt
@require_POST
def sap_orders_webhook(request: HttpRequest):  # type: ignore[no-untyped-def]
    """Endpoint pentru SAP (webhook) care primește comenzi și le importă.

    - Autorizare prin header `X-API-KEY` (sau `Authorization: Bearer <key>`)
    - Acceptă fie un obiect cu o singură comandă, fie o listă de comenzi
    - Returnează JSON cu număr de succes și erori
    """
    if not _authorized(request):
        return JsonResponse({"error": "unauthorized"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)

    orders = payload if isinstance(payload, list) else [payload]
    result = {"success": 0, "errors": []}
    for entry in orders:
        try:
            import_sap_order(entry)
            result["success"] += 1
        except Exception as exc:
            result["errors"].append(str(exc))

    status = 207 if result["errors"] else 200
    return JsonResponse(result, status=status)



