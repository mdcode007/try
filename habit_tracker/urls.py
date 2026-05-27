"""habit_tracker/urls.py — root URL configuration."""

from django.contrib import admin
from django.urls import path, include
from habit.views import SignUpView

urlpatterns = [
    path("admin/",    admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("",          include("habit.urls")),
    path("signup/",   SignUpView.as_view(), name="signup"),
]
