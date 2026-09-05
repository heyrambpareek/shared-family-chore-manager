# Shared Family Chore Manager

A small web application for households to assign, schedule, and track shared chores. Each family member has an individual account; adults manage household chores and children can see and complete only their own assignments.

## Project status

Tasks 1–3 are complete: Django foundation, household access, and adult chore creation/recurrence. Personal chore views and completion, reminder delivery, and production hardening remain planned work.

## Version-one scope

- Household creation and individual member accounts
- Adult and child roles with role-appropriate access
- One-person chore assignments with due dates and times
- One-time, daily, weekly, and monthly schedules
- Today, Upcoming, Overdue, and completion-history views
- Immediate completion by the assigned member
- Automatic next-occurrence creation for recurring chores
- Immutable completion history that survives later chore edits or deletion
- Email reminders 24 hours before due, at due time, and once one hour overdue

## Key rules

- All schedule calculations use the household timezone; an omitted due time defaults to 9:00 AM.
- A pending occurrence becomes overdue after its due date and time.
- Monthly schedules requested for unavailable dates run on that month's final calendar day.
- Completing a recurring occurrence creates the next one without changing the historical completion entry.
- Deleting a recurring chore prevents future occurrences but retains recorded history.

## Documentation

- [Product specification](spec.md)
- [Implementation plan](_docs/plan.md)

## Out of scope

Version one intentionally excludes shopping lists, budgeting, messaging, gamification, AI features, browser/push notifications, custom recurrence intervals, multi-assignee chores, and adult completion approval.

## Planned technology

The application will be implemented with Django. The concrete project structure, dependencies, background-job mechanism, and deployment settings will be chosen during implementation; see the plan for the proposed approach and decisions to validate first.

## Local setup

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Use environment variables such as `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `DJANGO_TIME_ZONE` to override the development defaults. See `.env.example` for the expected values; load those values through your local shell or deployment environment.
