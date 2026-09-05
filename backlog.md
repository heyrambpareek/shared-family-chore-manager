# Backlog

## 1. [x] Foundation — Django bootstrap

Create the Django project and an `accounts` app with a custom user model before the first migration. Add environment-based settings, a minimal base template and home route, dependency metadata, and a smoke test. Do not add household, membership, chore, scheduling, reminder, or authentication-flow features in this task.

## 2. [x] Households and access

Add households, adult/child memberships, registration/sign-in, member management, and authorization tests.

## 3. [x] Chore creation and recurrence

Implement chore series and occurrences, adult CRUD, validation, and one-time/daily/weekly/monthly schedule calculation.

## 4. Chore views and completion

Build Today, Upcoming, Overdue, and history views with role-scoped data access and atomic recurring completion.

## 5. Email reminders

Add durable, idempotent scheduling and email delivery for 24-hour, due-time, and one-hour-overdue reminders.

## 6. Hardening and deployment

Complete permission, recurrence, timezone, reminder, history, and concurrency coverage; document production deployment.
