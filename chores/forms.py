from datetime import time

from django import forms

from households.models import Membership

from .models import ChoreSeries, ChoreOccurrence


class ChoreSeriesForm(forms.ModelForm):
    recurrence_weekday = forms.TypedChoiceField(
        choices=[("", "---------")] + [(str(day), name) for day, name in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])],
        coerce=int,
        required=False,
    )
    recurrence_day = forms.TypedChoiceField(
        choices=[("", "---------")] + [(str(day), str(day)) for day in range(1, 32)],
        coerce=int,
        required=False,
    )

    class Meta:
        model = ChoreSeries
        fields = ("title", "description", "assignee", "schedule_type", "start_date", "due_time", "recurrence_weekday", "recurrence_day")
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "due_time": forms.TimeInput(attrs={"type": "time"})}

    def __init__(self, *args, household, **kwargs):
        super().__init__(*args, **kwargs)
        self.household = household
        self.fields["assignee"].queryset = Membership.objects.filter(household=household)
        self.fields["due_time"].required = False

    def clean(self):
        cleaned_data = super().clean()
        schedule_type = cleaned_data.get("schedule_type")
        weekday = cleaned_data.get("recurrence_weekday")
        day = cleaned_data.get("recurrence_day")
        if weekday == "":
            weekday = None
        if day == "":
            day = None
        cleaned_data["recurrence_weekday"] = weekday
        cleaned_data["recurrence_day"] = day
        if cleaned_data.get("due_time") is None:
            cleaned_data["due_time"] = time(9, 0)
        if schedule_type == ChoreSeries.ScheduleType.WEEKLY and weekday is None:
            self.add_error("recurrence_weekday", "Choose a weekday for a weekly chore.")
        if schedule_type == ChoreSeries.ScheduleType.MONTHLY and day is None:
            self.add_error("recurrence_day", "Choose a day for a monthly chore.")
        return cleaned_data

    def save(self, commit=True):
        series = super().save(commit=False)
        series.household = self.household
        if commit:
            series.full_clean()
            series.save()
        return series


def create_initial_occurrence(series: ChoreSeries) -> ChoreOccurrence:
    return ChoreOccurrence.objects.create(
        series=series,
        assignee=series.assignee,
        due_at=series.first_due_at(),
    )
