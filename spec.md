# Shared Family Chore Manager — Project Specification

## 1. Product purpose

Build a small, practical web application for families living together to manage shared household chores. It makes clear what each person needs to do, when it is due, and what has been completed.

## 2. Target users

Families who live in the same household. Every family member has an individual login and belongs to one family household.

## 3. Roles and permissions

### Adult

- Create, edit, and delete chores.
- Assign any chore to exactly one family member, adult or child.
- Set due dates and recurring schedules.
- View all household chores and all completion history.
- Manage household members.
- Edit or delete a completed chore without changing or removing its recorded completion-history entry.

### Child

- Sign in with their own account.
- View only chores assigned to them.
- View the status and schedule of their assigned chores.
- Mark their assigned chores complete immediately.
- Cannot create, edit, delete, reassign, or approve chores.

## 4. Core chore model

Each chore has:

- Title (required)
- Optional description
- One assignee (required)
- Due date and due time (required)
- Status: pending, completed, or overdue
- Schedule type: one-time, daily, weekly, or monthly
- Recurrence details when applicable
- Creation timestamp
- Completion timestamp and the family member who completed it

All times use the household's configured timezone. If no due time is chosen, the application defaults it to 9:00 AM in that timezone.

## 5. Scheduling rules

- One-time chores occur once on their due date.
- Daily chores recur every day.
- Weekly chores recur on an adult-selected day of the week.
- Monthly chores recur on an adult-selected day of the month.
- For a monthly schedule set to a date that does not occur in a given month (for example, the 31st), the occurrence is due on that month's last calendar day.
- When a recurring chore is completed, the app automatically creates the next scheduled occurrence for the same assignee.
- Completing a recurring occurrence does not alter its completion record.
- A chore is overdue when it remains pending after its due date and time.

## 6. Chore views

The app provides these focused views:

- **Today:** chores due today for the signed-in user; adults can also view the household's chores due today.
- **Upcoming:** pending chores due after today.
- **Overdue:** pending chores past their due date and time.
- **Completion history:** completed chores with chore title, assignee, scheduled due date, completion time, and completer.

Children see only their assigned chores and their own completion history. Adults see household-wide information.

## 7. Email reminders

Version one sends email only; browser and push notifications are out of scope.

For each chore occurrence, send the assignee:

- One reminder exactly 24 hours before its due date and time.
- One reminder at its due date and time.
- One additional reminder after it becomes overdue.

The overdue email is sent once, one hour after the chore becomes overdue. No repeated overdue reminders are sent. Reminders are not sent for an occurrence that has already been completed or deleted.

## 8. Completion history and edits

- Completing a chore creates an immutable completion-history entry.
- Adults may edit or delete the current chore record, including after completion.
- Editing or deleting a completed chore must never modify, remove, or erase its existing completion-history entry.
- Deleting a recurring chore stops future occurrences from being created; already-recorded completion history remains.

## 9. In scope for version one

- Account registration and sign-in for individual family members.
- Creating a household and adding family members.
- Adult and child roles with the permissions above.
- Manual, single-person chore assignment.
- One-time, daily, weekly, and monthly chores.
- Due dates/times, Today, Upcoming, and Overdue views.
- Immediate completion by the assigned person, including children.
- Automatic creation of the next recurring occurrence after completion.
- Completion history preserved independently of later chore changes.
- Email reminders at 24 hours before due, at due time, and once after overdue.

## 10. Explicitly out of scope

- Shopping lists
- Expenses, payments, bills, or budgets
- Chat, comments, or messaging
- Gamification, points, rewards, streaks, or leaderboards
- AI-generated chores, schedules, or recommendations
- Browser or push notifications
- Custom recurrence intervals
- Multi-assignee chores
- Adult approval before children can complete chores

## 11. Success criteria

An adult can create and manually assign a recurring or one-time chore in a few steps. Each family member can reliably see their work due today, upcoming work, and overdue work. Completing a recurring chore preserves the completion record and schedules the next occurrence automatically. Email reminders arrive at the defined times without repeated overdue messages.
