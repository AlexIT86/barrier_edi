from __future__ import annotations

from django.urls import path

from .views import (
    DeliveryCreateView,
    DeliveryDetailView,
    DeliveryListView,
    DeliveryValidateView,
)


app_name = "deliveries"

urlpatterns = [
    path("", DeliveryListView.as_view(), name="delivery_list"),
    path("create/", DeliveryCreateView.as_view(), name="delivery_create"),
    path("<int:pk>/", DeliveryDetailView.as_view(), name="delivery_detail"),
    path("<int:pk>/validate/", DeliveryValidateView.as_view(), name="delivery_validate"),
]


