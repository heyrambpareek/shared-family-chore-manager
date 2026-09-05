import calendar
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db import models
from django.utils import timezone

from households.models import Household, Membership


class ChoreSeries(models.Model):
    class ScheduleType(models.TextChoices):
        ONE_TIME = "one_time", "One-time"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chore_series")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="assigned_chore_series")
    schedule_type = models.CharField(max_length=10, choices=ScheduleType.choices)
    start_date = models.DateField()
    due_time = models.TimeField(default=time(9, 0))
    recurrence_weekday = models.PositiveSmallIntegerField(blank=True, null=True)
    recurrence_day = models.PositiveSmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        errors = {}
        if self.assignee_id and self.household_id and self.assignee.household_id != self.household_id:
            errors["assignee"] = "Assignee must belong to this household."
        if self.schedule_type == self.ScheduleType.WEEKLY:
            if self.recurrence_weekday is None or not 0 <= self.recurrence_weekday <= 6:
                errors["recurrence_weekday"] = "Choose a weekday for a weekly chore."
        elif self.recurrence_weekday is not None:
            errors["recurrence_weekday"] = "A weekday is only used for weekly chores."
        if self.schedule_type == self.ScheduleType.MONTHLY:
            if self.recurrence_day is None or not 1 <= self.recurrence_day <= 31:
                errors["recurrence_day"] = "Choose a day from 1 to 31 for a monthly chore."
        elif self.recurrence_day is not None:
            errors["recurrence_day"] = "A month day is only used for monthly chores."
        if errors:
            from django.core.exceptions import ValidationError
            raise ValidationError(errors)

    def first_due_date(self) -> date:
        if self.schedule_type == self.ScheduleType.WEEKLY:
            return self.start_date + timedelta(days=(self.recurrence_weekday - self.start_date.weekday()) % 7)
        if self.schedule_type == self.ScheduleType.MONTHLY:
            return monthly_date_on_or_after(self.start_date, self.recurrence_day)
        return self.start_date

    def first_due_at(self) -> datetime:
        local_due = datetime.combine(self.first_due_date(), self.due_time)
        return timezone.make_aware(local_due, ZoneInfo(self.household.timezone))

    def __str__(self) -> str:
        return self.title


class ChoreOccurrence(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"

    series = models.ForeignKey(ChoreSeries, on_delete=models.CASCADE, related_name="occurrences")
    assignee = models.ForeignKey(Membership, on_delete=models.PROTECT, related_name="assigned_occurrences")
    due_at = models.DateTimeField()
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["series", "due_at"], name="unique_series_due_at")]
        ordering = ["due_at"]

    def __str__(self) -> str:
        return f"{self.series}: {self.due_at}"


def monthly_date_on_or_after(start: date, requested_day: int) -> date:
    year, month = start.year, start.month
    while True:
        candidate = date(year, month, min(requested_day, calendar.monthrange(year, month)[1]))
        if candidate >= start:
            return candidate
        month += 1
        if month == 13:
            year, month = year + 1, 1
