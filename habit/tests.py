from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Habit, HabitCompletion


# Helpers

def make_user(username="user1", password="Testpass123!"):
    return User.objects.create_user(username=username, password=password)


def make_habit(user, name="Test Habit", periodicity=Habit.DAILY):
    return Habit.objects.create(
        name=name,
        description="Test description",
        user=user,
        periodicity=periodicity,
    )


def complete_on(habit, *days):
    for d in days:
        HabitCompletion.objects.get_or_create(habit=habit, date=d)


class HabitCompletionCheckTests(TestCase):

    def setUp(self):
        self.user   = make_user()
        self.daily  = make_habit(self.user, "Daily Habit",  Habit.DAILY)
        self.weekly = make_habit(self.user, "Weekly Habit", Habit.WEEKLY)
        self.today  = date.today()

    def test_daily_not_completed_by_default(self):
        self.assertFalse(self.daily.is_completed_on(self.today))

    def test_daily_completed_after_creation(self):
        complete_on(self.daily, self.today)
        self.assertTrue(self.daily.is_completed_on(self.today))

    def test_daily_does_not_bleed_to_next_day(self):
        complete_on(self.daily, self.today)
        self.assertFalse(self.daily.is_completed_on(self.today + timedelta(days=1)))

    def test_daily_does_not_bleed_to_previous_day(self):
        complete_on(self.daily, self.today)
        self.assertFalse(self.daily.is_completed_on(self.today - timedelta(days=1)))

    def test_weekly_any_day_in_week_counts(self):
        monday = self.today - timedelta(days=self.today.weekday())
        complete_on(self.weekly, monday + timedelta(days=4))
        self.assertTrue(self.weekly.is_completed_on(monday))

    def test_weekly_does_not_bleed_to_previous_week(self):
        complete_on(self.weekly, self.today)
        last_monday = self.today - timedelta(days=self.today.weekday() + 7)
        self.assertFalse(self.weekly.is_completed_in_week(last_monday))

    def test_is_completed_in_week_true(self):
        week_start = self.today - timedelta(days=self.today.weekday())
        complete_on(self.weekly, week_start + timedelta(days=2))
        self.assertTrue(self.weekly.is_completed_in_week(week_start))

    def test_is_completed_in_week_false_when_empty(self):
        week_start = self.today - timedelta(days=self.today.weekday())
        self.assertFalse(self.weekly.is_completed_in_week(week_start))


class CurrentStreakTests(TestCase):

    def setUp(self):
        self.user  = make_user()
        self.today = date.today()

    def test_daily_zero_when_empty(self):
        habit = make_habit(self.user, "Empty", Habit.DAILY)
        self.assertEqual(habit.current_streak, 0)

    def test_daily_one_day(self):
        habit = make_habit(self.user, "One", Habit.DAILY)
        complete_on(habit, self.today)
        self.assertEqual(habit.current_streak, 1)

    def test_daily_three_consecutive_days(self):
        habit = make_habit(self.user, "Three", Habit.DAILY)
        complete_on(
            habit,
            self.today,
            self.today - timedelta(days=1),
            self.today - timedelta(days=2),
        )
        self.assertEqual(habit.current_streak, 3)

    def test_daily_streak_breaks_on_gap(self):
        habit = make_habit(self.user, "Gap", Habit.DAILY)
        complete_on(habit, self.today, self.today - timedelta(days=2))
        self.assertEqual(habit.current_streak, 1)

    def test_daily_streak_zero_if_only_old_completion(self):
        habit = make_habit(self.user, "Old", Habit.DAILY)
        complete_on(habit, self.today - timedelta(days=5))
        self.assertEqual(habit.current_streak, 0)

    def test_weekly_one_week(self):
        habit = make_habit(self.user, "WkOne", Habit.WEEKLY)
        complete_on(habit, self.today)
        self.assertEqual(habit.current_streak, 1)

    def test_weekly_two_consecutive_weeks(self):
        habit        = make_habit(self.user, "WkTwo", Habit.WEEKLY)
        this_monday  = self.today - timedelta(days=self.today.weekday())
        last_monday  = this_monday - timedelta(weeks=1)
        complete_on(habit, this_monday, last_monday)
        self.assertEqual(habit.current_streak, 2)

    def test_weekly_zero_when_empty(self):
        habit = make_habit(self.user, "WkEmpty", Habit.WEEKLY)
        self.assertEqual(habit.current_streak, 0)


class LongestStreakTests(TestCase):

    def setUp(self):
        self.user  = make_user()
        self.today = date.today()

    def test_daily_zero_when_empty(self):
        habit = make_habit(self.user, "E", Habit.DAILY)
        self.assertEqual(habit.longest_streak, 0)

    def test_daily_single_completion(self):
        habit = make_habit(self.user, "S", Habit.DAILY)
        complete_on(habit, self.today)
        self.assertEqual(habit.longest_streak, 1)

    def test_daily_picks_longer_run(self):
        habit = make_habit(self.user, "L", Habit.DAILY)
        complete_on(
            habit,
            self.today,
            self.today - timedelta(days=1),
            self.today - timedelta(days=2),
            self.today - timedelta(days=4),
            self.today - timedelta(days=5),
        )
        self.assertEqual(habit.longest_streak, 3)

    def test_weekly_picks_longer_run(self):
        habit   = make_habit(self.user, "WL", Habit.WEEKLY)
        monday  = self.today - timedelta(days=self.today.weekday())
        complete_on(
            habit,
            monday,
            monday - timedelta(weeks=1),
            monday - timedelta(weeks=2),
            monday - timedelta(weeks=4),
        )
        self.assertEqual(habit.longest_streak, 3)

    def test_weekly_zero_when_empty(self):
        habit = make_habit(self.user, "WE", Habit.WEEKLY)
        self.assertEqual(habit.longest_streak, 0)


class StreakStartedTests(TestCase):

    def setUp(self):
        self.user  = make_user()
        self.today = date.today()

    def test_none_when_no_streak(self):
        habit = make_habit(self.user, "N", Habit.DAILY)
        self.assertIsNone(habit.streak_started)

    def test_today_when_streak_length_one(self):
        habit = make_habit(self.user, "O", Habit.DAILY)
        complete_on(habit, self.today)
        self.assertEqual(habit.streak_started, self.today)

    def test_correct_start_for_multi_day_streak(self):
        habit = make_habit(self.user, "M", Habit.DAILY)
        start = self.today - timedelta(days=2)
        complete_on(habit, self.today, self.today - timedelta(1), start)
        self.assertEqual(habit.streak_started, start)

    def test_weekly_returns_monday_of_oldest_week(self):
        habit        = make_habit(self.user, "WS", Habit.WEEKLY)
        this_monday  = self.today - timedelta(days=self.today.weekday())
        last_monday  = this_monday - timedelta(weeks=1)
        complete_on(habit, this_monday, last_monday)
        self.assertEqual(habit.streak_started, last_monday)


class HabitManagerTests(TestCase):

    def setUp(self):
        self.user  = make_user("owner")
        self.other = make_user("other")
        make_habit(self.user,  "My Daily",   Habit.DAILY)
        make_habit(self.user,  "My Weekly",  Habit.WEEKLY)
        make_habit(self.other, "Their Habit", Habit.DAILY)

    def test_for_user_returns_own_habits_only(self):
        qs = Habit.objects.for_user(self.user)
        self.assertEqual(qs.count(), 2)
        self.assertTrue(all(h.user == self.user for h in qs))

    def test_daily_for_user_filters_periodicity(self):
        qs = Habit.objects.daily_for_user(self.user)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "My Daily")

    def test_weekly_for_user_filters_periodicity(self):
        qs = Habit.objects.weekly_for_user(self.user)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "My Weekly")

    def test_for_user_does_not_return_other_users_habits(self):
        qs = Habit.objects.for_user(self.user)
        self.assertFalse(qs.filter(user=self.other).exists())


class AuthenticationTests(TestCase):

    def test_dashboard_redirects_unauthenticated(self):
        r = Client().get(reverse("dashboard"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r["Location"])

    def test_daily_view_redirects_unauthenticated(self):
        r = Client().get(reverse("daily_habit"))
        self.assertEqual(r.status_code, 302)

    def test_weekly_view_redirects_unauthenticated(self):
        r = Client().get(reverse("weekly_habit"))
        self.assertEqual(r.status_code, 302)

    def test_complete_habit_redirects_unauthenticated(self):
        user  = make_user("auth_owner")
        habit = make_habit(user)
        r     = Client().post(reverse("complete_habit", args=[habit.id]))
        self.assertEqual(r.status_code, 302)

    def test_cross_user_cannot_delete_habit(self):
        owner   = make_user("owner1")
        hacker  = make_user("hacker1")
        habit   = make_habit(owner, "Protected")

        c = Client()
        c.login(username="hacker1", password="Testpass123!")
        r = c.post(reverse("delete_habit", args=[habit.id]))

        self.assertEqual(r.status_code, 403)
        self.assertTrue(Habit.objects.filter(id=habit.id).exists())

    def test_cross_user_cannot_edit_habit(self):
        owner   = make_user("owner2")
        hacker  = make_user("hacker2")
        habit   = make_habit(owner, "Safe Habit")

        c = Client()
        c.login(username="hacker2", password="Testpass123!")
        r = c.post(
            reverse("edit_habit", args=[habit.id]),
            {"name": "Hacked", "description": "x", "periodicity": Habit.DAILY},
        )

        self.assertEqual(r.status_code, 403)
        habit.refresh_from_db()
        self.assertEqual(habit.name, "Safe Habit")

    def test_cross_user_cannot_view_analytics(self):
        owner  = make_user("owner3")
        hacker = make_user("hacker3")
        habit  = make_habit(owner, "Private")

        c = Client()
        c.login(username="hacker3", password="Testpass123!")
        r = c.get(reverse("detail_habit", args=[habit.id]))
        self.assertEqual(r.status_code, 403)


class HabitViewCRUDTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user   = make_user()
        self.client.login(username="user1", password="Testpass123!")
        self.habit  = make_habit(self.user, "Read Book")

    def test_dashboard_returns_200(self):
        r = self.client.get(reverse("dashboard"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard.html")

    def test_dashboard_shows_habit_name(self):
        r = self.client.get(reverse("dashboard"))
        self.assertContains(r, "Read Book")

    def test_create_habit_redirects_on_success(self):
        r = self.client.post(reverse("create_habit"), {
            "name": "Meditate", "description": "10 min", "periodicity": Habit.DAILY,
        })
        self.assertEqual(r.status_code, 302)

    def test_create_habit_persists_to_db(self):
        self.client.post(reverse("create_habit"), {
            "name": "Meditate", "description": "10 min", "periodicity": Habit.DAILY,
        })
        self.assertTrue(Habit.objects.filter(name="Meditate", user=self.user).exists())

    def test_edit_habit_updates_description(self):
        self.client.post(
            reverse("edit_habit", args=[self.habit.id]),
            {"name": "Read Book", "description": "50 pages", "periodicity": Habit.DAILY},
        )
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.description, "50 pages")

    def test_delete_habit_removes_from_db(self):
        self.client.post(reverse("delete_habit", args=[self.habit.id]))
        self.assertFalse(Habit.objects.filter(id=self.habit.id).exists())

    def test_daily_view_returns_200(self):
        r = self.client.get(reverse("daily_habit"))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "daily_habit.html")

    def test_daily_view_shows_daily_habits(self):
        r = self.client.get(reverse("daily_habit"))
        self.assertContains(r, "Read Book")

    def test_weekly_view_returns_200(self):
        weekly = make_habit(self.user, "Gym", Habit.WEEKLY)
        r = self.client.get(reverse("weekly_habit"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Gym")

    def test_detail_view_returns_200(self):
        r = self.client.get(reverse("detail_habit", args=[self.habit.id]))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "habit_detail.html")

    def test_home_view_accessible_without_login(self):
        r = Client().get(reverse("home"))
        self.assertEqual(r.status_code, 200)


class HabitCompletionAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user   = make_user()
        self.client.login(username="user1", password="Testpass123!")
        self.habit  = make_habit(self.user, "Exercise")
        self.today  = date.today()

    def test_complete_returns_200_and_success(self):
        r = self.client.post(reverse("complete_habit", args=[self.habit.id]))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["success"])

    def test_complete_creates_db_record(self):
        self.client.post(reverse("complete_habit", args=[self.habit.id]))
        self.assertTrue(
            HabitCompletion.objects.filter(habit=self.habit, date=self.today).exists()
        )

    def test_complete_twice_does_not_duplicate(self):
        self.client.post(reverse("complete_habit", args=[self.habit.id]))
        self.client.post(reverse("complete_habit", args=[self.habit.id]))
        count = HabitCompletion.objects.filter(habit=self.habit, date=self.today).count()
        self.assertEqual(count, 1)

    def test_complete_returns_current_streak(self):
        r    = self.client.post(reverse("complete_habit", args=[self.habit.id]))
        data = r.json()
        self.assertIn("current_streak", data)
        self.assertEqual(data["current_streak"], 1)

    def test_undo_removes_db_record(self):
        HabitCompletion.objects.create(habit=self.habit, date=self.today)
        self.client.post(reverse("undo_complete_habit", args=[self.habit.id]))
        self.assertFalse(
            HabitCompletion.objects.filter(habit=self.habit, date=self.today).exists()
        )

    def test_undo_returns_success_true(self):
        HabitCompletion.objects.create(habit=self.habit, date=self.today)
        r = self.client.post(reverse("undo_complete_habit", args=[self.habit.id]))
        self.assertTrue(r.json()["success"])

    def test_undo_when_not_done_returns_404(self):
        r = self.client.post(reverse("undo_complete_habit", args=[self.habit.id]))
        self.assertEqual(r.status_code, 404)

    def test_complete_get_request_returns_405(self):
        r = self.client.get(reverse("complete_habit", args=[self.habit.id]))
        self.assertEqual(r.status_code, 405)
