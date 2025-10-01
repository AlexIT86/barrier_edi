from __future__ import annotations

from django.urls import path

from .views import (
    PartnerDashboardView,
    PartnerLoginView,
    PartnerLogoutView,
    PartnerOrderDetailView,
    PartnerOrderListView,
    partners_admin,
    PartnerProfileView,
)


app_name = "partners"

urlpatterns = [
    path("login/", PartnerLoginView.as_view(), name="login"),
    path("logout/", PartnerLogoutView.as_view(), name="logout"),
    path("dashboard/", PartnerDashboardView.as_view(), name="dashboard"),
    path("orders/", PartnerOrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", PartnerOrderDetailView.as_view(), name="order_detail"),
    path("admin-page/", partners_admin, name="admin_page"),
    path("profile/", PartnerProfileView.as_view(), name="profile"),
]


