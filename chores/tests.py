from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, Membership

from .models import ChoreSeries, ChoreOccurrence, monthly_date_on_or_after


class ChoreCreationTests(TestCase):
    def setUp(self) -> None:
        self.household = Household.objects.create(name="Home", timezone="UTC")
        self.adult = get_user_model().objects.create_user("adult", password="test-password")
        self.child = get_user_model().objects.create_user("child", password="test-password")
        self.adult_membership = Membership.objects.create(household=self.household, user=self.adult, role="adult")
        self.child_membership = Membership.objects.create(household=self.household, user=self.child, role="child")

    def test_adult_creates_weekly_chore_and_initial_occurrence(self) -> None:
        self.client.force_login(self.adult)
        response = self.client.post(reverse("chores:create"), {"title": "Bins", "description": "", "assignee": self.child_membership.pk, "schedule_type": "weekly", "start_date": "2026-09-01", "due_time": "09:00", "recurrence_weekday": "4", "recurrence_day": ""})

        self.assertRedirects(response, reverse("chores:list"))
        occurrence = ChoreOccurrence.objects.get(series__title="Bins")
        self.assertEqual(occurrence.due_at.date(), date(2026, 9, 4))
        self.assertEqual(occurrence.assignee, self.child_membership)

    def test_missing_due_time_defaults_to_nine_am(self) -> None:
        self.client.force_login(self.adult)
        response = self.client.post(reverse("chores:create"), {"title": "Dishes", "description": "", "assignee": self.child_membership.pk, "schedule_type": "one_time", "start_date": "2026-09-01", "due_time": "", "recurrence_weekday": "", "recurrence_day": ""})

        self.assertRedirects(response, reverse("chores:list"))
        self.assertEqual(ChoreOccurrence.objects.get(series__title="Dishes").due_at.time(), time(9, 0))

    def test_child_cannot_create_or_edit_chores(self) -> None:
        series = ChoreSeries.objects.create(household=self.household, title="Wash", assignee=self.child_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        self.client.force_login(self.child)

        self.assertEqual(self.client.get(reverse("chores:create")).status_code, 403)
        self.assertEqual(self.client.get(reverse("chores:edit", args=[series.pk])).status_code, 403)

    def test_child_cannot_delete_a_chore_with_a_post_request(self) -> None:
        series = ChoreSeries.objects.create(household=self.household, title="Wash", assignee=self.child_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        self.client.force_login(self.child)

        response = self.client.post(reverse("chores:delete", args=[series.pk]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(ChoreSeries.objects.get(pk=series.pk).is_active)

    def test_adult_cannot_edit_or_delete_another_households_chore(self) -> None:
        other_household = Household.objects.create(name="Other", timezone="UTC")
        other_adult = get_user_model().objects.create_user("other-adult", password="test-password")
        other_child = get_user_model().objects.create_user("other-child", password="test-password")
        Membership.objects.create(household=other_household, user=other_adult, role="adult")
        other_child_membership = Membership.objects.create(household=other_household, user=other_child, role="child")
        other_series = ChoreSeries.objects.create(household=other_household, title="Private", assignee=other_child_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        self.client.force_login(self.adult)

        self.assertEqual(self.client.get(reverse("chores:edit", args=[other_series.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("chores:delete", args=[other_series.pk])).status_code, 404)
        self.assertTrue(ChoreSeries.objects.get(pk=other_series.pk).is_active)

    def test_assignee_field_excludes_other_households(self) -> None:
        other = Household.objects.create(name="Other", timezone="UTC")
        outsider = get_user_model().objects.create_user("outsider", password="test-password")
        outsider_membership = Membership.objects.create(household=other, user=outsider, role="child")
        self.client.force_login(self.adult)

        response = self.client.post(reverse("chores:create"), {"title": "Bad", "assignee": outsider_membership.pk, "schedule_type": "one_time", "start_date": "2026-09-01", "due_time": "09:00", "recurrence_weekday": "", "recurrence_day": ""})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ChoreSeries.objects.filter(title="Bad").exists())

    def test_child_list_contains_only_chores_assigned_to_that_child(self) -> None:
        another_child = get_user_model().objects.create_user("another-child", password="test-password")
        another_membership = Membership.objects.create(household=self.household, user=another_child, role="child")
        ChoreSeries.objects.create(household=self.household, title="Mine", assignee=self.child_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        ChoreSeries.objects.create(household=self.household, title="Theirs", assignee=another_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        self.client.force_login(self.child)

        response = self.client.get(reverse("chores:list"))

        self.assertContains(response, "Mine")
        self.assertNotContains(response, "Theirs")

    def test_edit_replaces_the_pending_occurrence_with_updated_schedule(self) -> None:
        series = ChoreSeries.objects.create(household=self.household, title="Bins", assignee=self.child_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        ChoreOccurrence.objects.create(series=series, assignee=self.child_membership, due_at="2026-09-01T09:00:00Z")
        self.client.force_login(self.adult)

        response = self.client.post(reverse("chores:edit", args=[series.pk]), {"title": "Bins", "description": "", "assignee": self.child_membership.pk, "schedule_type": "monthly", "start_date": "2026-02-01", "due_time": "10:30", "recurrence_weekday": "", "recurrence_day": "31"})

        self.assertRedirects(response, reverse("chores:list"))
        self.assertEqual(ChoreOccurrence.objects.filter(series=series).count(), 1)
        occurrence = ChoreOccurrence.objects.get(series=series)
        self.assertEqual(occurrence.due_at.date(), date(2026, 2, 28))
        self.assertEqual(occurrence.due_at.time(), time(10, 30))

    def test_delete_deactivates_series_and_removes_it_from_the_list(self) -> None:
        series = ChoreSeries.objects.create(household=self.household, title="Bins", assignee=self.child_membership, schedule_type="one_time", start_date=date(2026, 9, 1), due_time=time(9))
        self.client.force_login(self.adult)

        response = self.client.post(reverse("chores:delete", args=[series.pk]))

        self.assertRedirects(response, reverse("chores:list"))
        self.assertFalse(ChoreSeries.objects.get(pk=series.pk).is_active)
        self.assertNotContains(self.client.get(reverse("chores:list")), "Bins")


class RecurrenceCalculationTests(TestCase):
    def test_weekly_monday_is_valid_and_keeps_weekday_zero(self) -> None:
        household = Household.objects.create(name="Home", timezone="UTC")
        user = get_user_model().objects.create_user("adult", password="test-password")
        child = get_user_model().objects.create_user("child", password="test-password")
        Membership.objects.create(household=household, user=user, role="adult")
        child_membership = Membership.objects.create(household=household, user=child, role="child")
        self.client.force_login(user)

        response = self.client.post(reverse("chores:create"), {"title": "Monday task", "description": "", "assignee": child_membership.pk, "schedule_type": "weekly", "start_date": "2026-09-01", "due_time": "09:00", "recurrence_weekday": "0", "recurrence_day": ""})

        self.assertRedirects(response, reverse("chores:list"))
        self.assertEqual(ChoreOccurrence.objects.get(series__title="Monday task").due_at.date(), date(2026, 9, 7))

    def test_daily_schedule_uses_the_selected_start_date(self) -> None:
        household = Household.objects.create(name="Home", timezone="UTC")
        user = get_user_model().objects.create_user("adult", password="test-password")
        child = get_user_model().objects.create_user("child", password="test-password")
        Membership.objects.create(household=household, user=user, role="adult")
        child_membership = Membership.objects.create(household=household, user=child, role="child")
        self.client.force_login(user)

        response = self.client.post(reverse("chores:create"), {"title": "Daily task", "description": "", "assignee": child_membership.pk, "schedule_type": "daily", "start_date": "2026-09-01", "due_time": "09:00", "recurrence_weekday": "", "recurrence_day": ""})

        self.assertRedirects(response, reverse("chores:list"))
        self.assertEqual(ChoreOccurrence.objects.get(series__title="Daily task").due_at.date(), date(2026, 9, 1))

    def test_weekly_schedule_requires_a_weekday(self) -> None:
        household = Household.objects.create(name="Home", timezone="UTC")
        user = get_user_model().objects.create_user("adult", password="test-password")
        child = get_user_model().objects.create_user("child", password="test-password")
        Membership.objects.create(household=household, user=user, role="adult")
        child_membership = Membership.objects.create(household=household, user=child, role="child")
        self.client.force_login(user)

        response = self.client.post(reverse("chores:create"), {"title": "Invalid weekly", "description": "", "assignee": child_membership.pk, "schedule_type": "weekly", "start_date": "2026-09-01", "due_time": "09:00", "recurrence_weekday": "", "recurrence_day": ""})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ChoreSeries.objects.filter(title="Invalid weekly").exists())

    def test_monthly_31st_uses_last_day_of_february(self) -> None:
        self.assertEqual(monthly_date_on_or_after(date(2026, 2, 1), 31), date(2026, 2, 28))

    def test_monthly_date_advances_when_current_month_has_passed(self) -> None:
        self.assertEqual(monthly_date_on_or_after(date(2026, 2, 28), 15), date(2026, 3, 15))
