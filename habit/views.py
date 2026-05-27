from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .models import Habit, HabitCompletion


def _split_habits(habits, today: date):
    """Split habits into (incomplete, complete) for the given day."""
    incomplete = [h for h in habits if not h.is_completed_on(today)]
    complete   = [h for h in habits if     h.is_completed_on(today)]
    return incomplete, complete


def home(request):
    return render(request, "home.html")


class SignUpView(CreateView):
    form_class   = UserCreationForm
    success_url  = reverse_lazy("login")
    template_name = "signup.html"


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restricts a view to the habit's owner. Others get 403."""
    def test_func(self):
        return self.get_object().user == self.request.user


class Dashboard(LoginRequiredMixin, ListView):
    model               = Habit
    context_object_name = "habits"
    template_name       = "dashboard.html"

    def get_queryset(self):
        return Habit.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today   = date.today()
        habits  = context["habits"]

        context["incomplete_habits"], context["completed_habits"] = (
            _split_habits(habits, today)
        )
        context["today"] = today
        context["longest_streak_habit"] = (
            max(habits, key=lambda h: h.longest_streak) if habits else None
        )
        return context


class HabitCreateView(LoginRequiredMixin, CreateView):
    model         = Habit
    fields        = ["name", "description", "periodicity"]
    success_url   = reverse_lazy("dashboard")
    template_name = "create_habit.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class HabitUpdateView(OwnerRequiredMixin, UpdateView):
    model         = Habit
    fields        = ["name", "description", "periodicity"]
    success_url   = reverse_lazy("dashboard")
    template_name = "edit_habit.html"


class HabitDeleteView(OwnerRequiredMixin, DeleteView):
    model       = Habit
    success_url = reverse_lazy("dashboard")
    template_name = "delete_habit.html"


class HabitDetailView(OwnerRequiredMixin, DetailView):
    model               = Habit
    template_name       = "habit_detail.html"
    context_object_name = "habit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habit   = self.object
        today   = date.today()

        calendar_days = [
            {
                "date":      today - timedelta(days=i),
                "completed": habit.is_completed_on(today - timedelta(days=i)),
            }
            for i in range(29, -1, -1)
        ]

        context["calendar_days"]   = calendar_days
        context["current_streak"]  = habit.current_streak
        context["longest_streak"]  = habit.longest_streak
        context["streak_started"]  = habit.streak_started
        context["weekdays"] = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        return context


@login_required
def daily_habit(request):
    today   = date.today()
    habits  = Habit.objects.daily_for_user(request.user)
    incomplete, complete = _split_habits(habits, today)

    return render(request, "daily_habit.html", {
        "incomplete_habits": incomplete,
        "completed_habits":  complete,
        "user":  request.user,
        "today": today,
    })


@login_required
def weekly_habit(request):
    today   = date.today()
    habits  = Habit.objects.weekly_for_user(request.user)
    incomplete, complete = _split_habits(habits, today)

    return render(request, "weekly_habit.html", {
        "incomplete_habits": incomplete,
        "completed_habits":  complete,
        "user":  request.user,
        "today": today,
    })


@require_POST
@login_required
def complete_habit(request, habit_id: int):
    habit       = get_object_or_404(Habit, id=habit_id, user=request.user)
    today       = timezone.now().date()
    already_done = habit.is_completed_on(today)

    if not already_done:
        HabitCompletion.objects.create(habit=habit, date=today)

    return JsonResponse({
        "success":          True,
        "already_completed": already_done,
        "current_streak":   habit.current_streak,
    })


@require_POST
@login_required
def undo_complete_habit(request, habit_id: int):
    habit         = get_object_or_404(Habit, id=habit_id, user=request.user)
    today         = timezone.now().date()
    deleted, _    = habit.completions.filter(date=today).delete()

    if deleted:
        return JsonResponse({
            "success":        True,
            "message":        "Habit unmarked for today.",
            "current_streak": habit.current_streak,
        })

    return JsonResponse(
        {"success": False, "error": "No completion found for today."},
        status=404,
    )
