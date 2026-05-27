"""habit/urls.py — URL patterns for the habit app."""

from django.urls import path
from . import views

urlpatterns = [
    path("",                                        views.home,                      name="home"),
    path("habit/dashboard/",                        views.Dashboard.as_view(),       name="dashboard"),
    path("habit/create/",                           views.HabitCreateView.as_view(), name="create_habit"),
    path("habit/edit/<int:pk>/",                    views.HabitUpdateView.as_view(), name="edit_habit"),
    path("habit/delete/<int:pk>/",                  views.HabitDeleteView.as_view(), name="delete_habit"),
    path("habit/analytics/<int:pk>/",               views.HabitDetailView.as_view(), name="detail_habit"),
    path("habit/complete/<int:habit_id>/",          views.complete_habit,            name="complete_habit"),
    path("habit/undo-complete/<int:habit_id>/",     views.undo_complete_habit,       name="undo_complete_habit"),
    path("daily/",                                  views.daily_habit,               name="daily_habit"),
    path("weekly/",                                 views.weekly_habit,              name="weekly_habit"),
]
