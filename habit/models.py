from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    """Adds created_at and updated_at to any model that inherits from it."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HabitManager(models.Manager):
    """Custom manager — keeps filter logic off the views."""

    def for_user(self, user):
        return self.filter(user=user)

    def daily_for_user(self, user):
        return self.filter(user=user, periodicity=Habit.DAILY)

    def weekly_for_user(self, user):
        return self.filter(user=user, periodicity=Habit.WEEKLY)


class Habit(TimeStampedModel):
    """A trackable habit owned by a single user."""

    DAILY  = "daily"
    WEEKLY = "weekly"

    PERIODICITY_CHOICES = [
        (DAILY,  "Daily"),
        (WEEKLY, "Weekly"),
    ]

    name        = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True)
    user        = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="habits",
    )
    periodicity = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default=DAILY,
    )

    objects = HabitManager()

    class Meta:
        # Two users can share the same habit name
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_periodicity_display()})"

    def __repr__(self):
        return (
            f"<Habit id={self.pk} name={self.name!r} "
            f"user_id={self.user_id} periodicity={self.periodicity!r}>"
        )

    def is_completed_on(self, day: date) -> bool:
        """True if the habit counts as done on the given day."""
        if self.periodicity == self.DAILY:
            return self.completions.filter(date=day).exists()

        if self.periodicity == self.WEEKLY:
            week_start = day - timedelta(days=day.weekday())
            week_end   = week_start + timedelta(days=6)
            return self.completions.filter(
                date__range=(week_start, week_end)
            ).exists()

        return False

    def is_completed_in_week(self, week_start: date) -> bool:
        """True if at least one completion exists in the 7-day window starting on week_start."""
        return self.completions.filter(
            date__gte=week_start,
            date__lt=week_start + timedelta(days=7),
        ).exists()

    @property
    def current_streak(self) -> int:
        """Consecutive periods completed up to and including today."""
        today  = date.today()
        streak = 0

        if self.periodicity == self.DAILY:
            offset = 0
            while self.is_completed_on(today - timedelta(days=offset)):
                streak += 1
                offset += 1

        elif self.periodicity == self.WEEKLY:
            week   = today - timedelta(days=today.weekday())
            offset = 0
            while self.is_completed_in_week(week - timedelta(weeks=offset)):
                streak += 1
                offset += 1

        return streak

    @property
    def longest_streak(self) -> int:
        """Longest consecutive-period streak across all time."""
        if self.periodicity == self.DAILY:
            return self._longest_daily_streak()
        if self.periodicity == self.WEEKLY:
            return self._longest_weekly_streak()
        return 0

    @property
    def streak_started(self):
        """Date the current streak began, or None if no streak exists."""
        today  = date.today()

        if self.periodicity == self.DAILY:
            offset = 0
            while self.is_completed_on(today - timedelta(days=offset)):
                offset += 1
            return (today - timedelta(days=offset - 1)) if offset else None

        if self.periodicity == self.WEEKLY:
            week   = today - timedelta(days=today.weekday())
            offset = 0
            while self.is_completed_in_week(week - timedelta(weeks=offset)):
                offset += 1
            return (week - timedelta(weeks=offset - 1)) if offset else None

        return None

    def _longest_daily_streak(self) -> int:
        longest = current = 0
        previous = None

        for c in self.completions.order_by("date"):
            if previous and (c.date - previous).days == 1:
                current += 1
            else:
                current = 1
            longest  = max(longest, current)
            previous = c.date

        return longest

    def _longest_weekly_streak(self) -> int:
        weeks = set()
        for c in self.completions.all():
            iso_year, iso_week, _ = c.date.isocalendar()
            weeks.add((iso_year, iso_week))

        if not weeks:
            return 0

        longest = current = 0
        sorted_weeks = sorted(weeks)

        for i, (year, week) in enumerate(sorted_weeks):
            if i == 0:
                current = 1
            else:
                py, pw = sorted_weeks[i - 1]
                consecutive = (year == py and week == pw + 1) or (
                    year == py + 1 and pw >= 52 and week == 1
                )
                current = current + 1 if consecutive else 1
            longest = max(longest, current)

        return longest


class HabitCompletion(TimeStampedModel):
    """Records a single completion: one habit on one calendar date."""

    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    date = models.DateField()

    class Meta:
        unique_together = ("habit", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.habit.name} — {self.date}"

    def __repr__(self):
        return f"<HabitCompletion habit_id={self.habit_id} date={self.date}>"
