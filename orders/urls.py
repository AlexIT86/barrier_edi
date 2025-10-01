from __future__ import annotations

from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView
from .views import order_items_api
from .api import sap_orders_webhook


app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("<int:order_id>/items-api/", order_items_api, name="order_items_api"),
    path("api/sap/webhook/", sap_orders_webhook, name="sap_webhook"),
]


