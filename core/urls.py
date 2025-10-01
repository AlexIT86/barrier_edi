from __future__ import annotations

from django.urls import path
from .views import HomeView, StaffLoginView, StaffPasswordResetView, StaffProfileView, staff_logout


app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("login/", StaffLoginView.as_view(), name="staff_login"),
    path("reset/", StaffPasswordResetView.as_view(), name="staff_reset"),
    path("profile/", StaffProfileView.as_view(), name="staff_profile"),
    path("logout/", staff_logout, name="staff_logout"),
]


