<<<<<<< HEAD
<<<<<<< HEAD
# TRAC — Habit Tracker

> **Build consistency. Track progress. Stay accountable.**

TRAC is a full-stack web application built with Django that enables users to create, track, and analyse personal habits. The system supports both daily and weekly habit cycles, automatically computes streak metrics, and provides a clean, responsive interface for long-term habit management.

---

## Overview

TRAC is designed around a simple principle: **consistency over intensity**. The application provides users with actionable insights into their behaviour through streak tracking, historical visualization, and structured habit categorisation.

Each user operates in an isolated environment where they can:

* Define habits
* Track completion in real time
* Analyse performance over time

---

## Key Features

### Habit Management

* Create, edit, and delete habits
* Support for **daily** and **weekly** periodicity
* Per-user data isolation

### Real-Time Tracking

* One-click completion and undo functionality
* Asynchronous updates via Fetch API (no page reload)

### Streak Analytics

* Current streak calculation
* Longest streak tracking
* Automatic streak start detection

### Data Visualization

* 30-day completion calendar per habit
* Visual distinction between completed and missed days

### Dashboard Experience

* Segregation of completed and incomplete habits
* Dedicated views for daily and weekly habits
* Highlighting of highest-performing habit

### Authentication & Access Control

* User registration and login
* Ownership-based access restrictions
* Protected routes for all habit operations

---

## Tech Stack

| Layer                  | Technology         |
| ---------------------- | ------------------ |
| Backend                | Django 5.1         |
| Language               | Python 3.10+       |
| Database (Development) | SQLite             |
| Database (Production)  | PostgreSQL         |
| Styling                | Tailwind CSS (CDN) |
| Static File Serving    | WhiteNoise         |
| Application Server     | Gunicorn           |
| Environment Management | python-dotenv      |

---

## Architecture & Design

TRAC follows a **modular, layered architecture** consistent with standard Django practices.

### Application Structure

```
trac/
├── habit/                # Core domain logic (models, views, tests)
├── habit_tracker/        # Project configuration
├── templates/            # Presentation layer
├── static/               # Frontend assets
├── manage.py             # CLI entry point
```

---

### Domain Model

#### Habit

Represents a user-defined behaviour to be tracked.

* `name` — unique per user
* `description` — optional metadata
* `periodicity` — daily or weekly
* `user` — ownership relationship
* timestamps — creation and modification

#### HabitCompletion

Represents a completed instance of a habit.

* `habit` — foreign key relationship
* `date` — completion date
* unique constraint ensures one completion per day

---

### Object-Oriented Design

* **Abstract Base Model**
  Shared timestamp logic via a reusable base class

* **Custom Query Manager**
  Encapsulates common filtering logic (`for_user`, `daily`, `weekly`)

* **Computed Properties**
  Streak values exposed as properties for clean template access

* **Separation of Concerns**
  Business logic is contained within models, not views

---

## Streak Calculation Logic

### Daily Habits

* Counts consecutive calendar days
* Iterates backward from today
* Stops at first missed day

### Weekly Habits

* Based on ISO week definitions (Monday–Sunday)
* A week counts if at least one completion exists
* Tracks consecutive completed weeks

### Longest Streak

* Computed from historical completion records
* Resets on gaps in sequence
* Supports both daily and weekly modes

---

## Installation & Setup

### Prerequisites

* Python 3.10+
* Git

---

### 1. Clone the repository

```bash
git clone <repository-url>
cd trac
```

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

```bash
cp .env.example .env
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Update `.env`:

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

---

### 5. Apply migrations

```bash
python manage.py migrate
```

---

### 6. Create superuser

```bash
python manage.py createsuperuser
```

---

### 7. Run development server

```bash
python manage.py runserver
```

Access the application:

```
http://127.0.0.1:8000
```

---

## Usage

### Creating Habits

Users can define habits with a name, description, and periodicity.

### Tracking Progress

Habits can be marked complete or undone instantly via the dashboard.

### Viewing Analytics

Each habit includes a detailed analytics page displaying:

* Current streak
* Longest streak
* Streak start date
* 30-day history

---

## API Endpoints

### Complete Habit

```
POST /habit/complete/<id>/
```

**Response**

```json
{
  "success": true,
  "already_completed": false,
  "current_streak": 5
}
```

---

### Undo Completion

```
POST /habit/undo-complete/<id>/
```

**Response**

```json
{
  "success": true,
  "current_streak": 4
}
```

---

## Security Considerations

* Authentication required for all habit operations
* Ownership validation enforced at the view level
* CSRF protection enabled for all POST endpoints
* No cross-user data access permitted

---

## Deployment

For production environments:

* Switch database to PostgreSQL
* Set `DEBUG=False`
* Configure `ALLOWED_HOSTS`
* Use Gunicorn as the WSGI server
* Serve static files with WhiteNoise

---

## License

This project is intended for educational and personal use.
=======
# International-university_of_applied_science_project
>>>>>>> f9509b7f8c0ce11bd64b8cdc09d9de9d24cc8ff5
=======

>>>>>>> abd979236cb39310062b6b18457fcbc41c8d4f06
