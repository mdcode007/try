"""habit/admin.py — Django admin configuration."""

from django.contrib import admin
from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display  = ("name", "user", "periodicity", "created_at")
    list_filter   = ("periodicity",)
    search_fields = ("name", "user__username")
    ordering      = ("user", "name")


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display  = ("habit", "date")
    list_filter   = ("habit", "date")
    search_fields = ("habit__name",)
    ordering      = ("-date",)
