from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Habit",
            fields=[
                ("id",          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at",  models.DateTimeField(auto_now_add=True)),
                ("updated_at",  models.DateTimeField(auto_now=True)),
                ("name",        models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, max_length=1000)),
                ("periodicity", models.CharField(
                    choices=[("daily", "Daily"), ("weekly", "Weekly")],
                    default="daily",
                    max_length=10,
                )),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="habits",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                "ordering": ["name"],
                "unique_together": {("user", "name")},
            },
        ),
        migrations.CreateModel(
            name="HabitCompletion",
            fields=[
                ("id",         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("date",       models.DateField()),
                ("habit",      models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="completions",
                    to="habit.habit",
                )),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("habit", "date")},
            },
        ),
    ]
