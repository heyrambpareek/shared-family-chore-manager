# Implementation Plan

## Goal

Deliver a Django-based shared household chore manager that honors [the product specification](../spec.md), with reliable schedule calculations, role-based visibility, durable history, and email reminders.

## Proposed architecture

- **Django project:** server-rendered Django application with a custom user model from the first migration.
- **Database:** PostgreSQL in deployed environments. SQLite may be used only for local development.
- **Background work:** a durable scheduled-job system (for example, Celery with Redis or a database-backed scheduler) for reminder delivery and overdue state processing. Select the exact mechanism before implementation based on deployment constraints.
- **Timezone handling:** store timestamps as timezone-aware UTC values; calculate and display dates/times in each household's configured IANA timezone.
- **Email:** use Django's email backend behind a small reminder-delivery service so development and production providers can differ safely.

## Domain model

The precise names may change, but the following responsibilities should remain separate.

| Model | Responsibility |
| --- | --- |
| `User` | Login identity and account details. |
| `Household` | Family grouping and configured timezone. |
| `Membership` | Connects a user to one household and records the `adult` or `child` role. |
| `ChoreSeries` | The editable chore definition: title, description, assignee, schedule, and active/deleted state. |
| `ChoreOccurrence` | A concrete scheduled unit of work, with due timestamp, status, completion data, and reminder-send flags. |
| `CompletionHistory` | Immutable snapshot created on completion, retaining title, assignee, scheduled due time, completion time, and completer independently of later edits/deletes. |

Use a single assignee foreign key on the series and copy it to each occurrence. For recurring work, create the next occurrence only when the current occurrence is completed. A one-time series has one occurrence.

## Scheduling and state rules

1. Require a due date and assignee. Combine a missing due time with 9:00 AM in the household timezone.
2. Generate one-time, daily, weekly, or monthly occurrence due dates. Weekly uses the selected weekday; monthly uses the selected day or the month's final day when needed.
3. Treat an occurrence as overdue when it is pending and its due timestamp is in the past. Prefer deriving this at query/display time; a scheduled task may update a stored status only if it is needed for indexing or reporting.
4. On completion, atomically mark the occurrence complete, record its completion timestamp and completer, insert a history snapshot, and generate exactly one next occurrence for active recurring series.
5. Deleting a current series/occurrence must not delete history. Deactivating a recurring series prevents new occurrences.

## Authorization matrix

| Action | Adult | Child |
| --- | --- | --- |
| View household chores and history | Yes | No |
| View own chores and history | Yes | Yes |
| Create, edit, delete, or reassign chores | Yes | No |
| Manage household members | Yes | No |
| Complete own assigned occurrence | Yes | Yes |
| Complete another member's occurrence | Decide explicitly during implementation; default to no | No |

Enforce household membership and role checks in every query and mutation, not only in templates. The unresolved adult-completion policy above should be confirmed before coding.

## Reminder design

For every pending, non-deleted occurrence, schedule or discover three candidate events:

- 24 hours before the due timestamp
- At the due timestamp
- One hour after the due timestamp, only if still pending

Before sending, re-read the occurrence under a transaction or lock and skip it if completed/deleted or if that reminder type was already recorded as sent. Persist per-reminder sent timestamps (or a unique reminder-log record) to ensure retries do not create duplicate emails. Test timezone and daylight-saving transitions.

## Delivery phases

1. **Foundation:** initialize Django, custom user model, settings, environment configuration, base templates, and test tooling.
2. **Households and access:** create households, memberships, registration/sign-in, adult member management, and authorization tests.
3. **Chore creation and scheduling:** implement series/occurrence models, forms, validations, recurrence calculator, and adult CRUD.
4. **Personal views and completion:** build Today, Upcoming, Overdue, and History views with role-based query scopes; implement atomic completion and next-occurrence generation.
5. **Reminders:** implement email templates, scheduler integration, idempotent delivery records, and operational error logging.
6. **Hardening:** add end-to-end permission, recurrence edge-case, timezone, reminder, edit/delete-history, and concurrency tests; then prepare deployment documentation.

## Acceptance tests

- An adult can assign one-time and recurring chores to any household member.
- A child can see only their own occurrences and can complete only an occurrence assigned to them.
- A recurring completion preserves an immutable history snapshot and creates the correct next occurrence exactly once.
- Weekly and monthly dates follow the requested recurrence rules, including 29th–31st month-end behavior.
- Adults can change/delete current records without losing past completion history.
- Today, Upcoming, and Overdue views apply the household timezone and exclude unauthorized household data.
- Each eligible occurrence receives at most one reminder of each required type; no reminder is sent after completion or deletion.

## Decisions to confirm before implementation

- Production hosting and email provider, which determine the most suitable job scheduler.
- Whether an adult may complete chores assigned to someone else.
- Household invitation/join flow and whether a member may belong to more than one household.
- Desired account recovery and email-verification requirements.
