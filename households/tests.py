from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Household, Membership


class HouseholdAccessTests(TestCase):
    def setUp(self) -> None:
        self.household = Household.objects.create(name="Home", timezone="UTC")
        self.adult = get_user_model().objects.create_user("adult", password="test-password")
        self.child = get_user_model().objects.create_user("child", password="test-password")
        Membership.objects.create(household=self.household, user=self.adult, role="adult")
        Membership.objects.create(household=self.household, user=self.child, role="child")

    def test_adult_can_add_a_child_member(self) -> None:
        self.client.force_login(self.adult)

        response = self.client.post(
            reverse("households:member-create"),
            {"username": "new-child", "email": "", "role": "child", "password1": "Strong-test-password-123", "password2": "Strong-test-password-123"},
        )

        self.assertRedirects(response, reverse("households:members"))
        self.assertEqual(Membership.objects.get(user__username="new-child").household, self.household)

    def test_child_cannot_manage_members(self) -> None:
        self.client.force_login(self.child)

        response = self.client.get(reverse("households:members"))

        self.assertEqual(response.status_code, 403)

    def test_child_cannot_create_members_with_a_post_request(self) -> None:
        self.client.force_login(self.child)

        response = self.client.post(
            reverse("households:member-create"),
            {"username": "unauthorized", "role": "child", "password1": "Strong-test-password-123", "password2": "Strong-test-password-123"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(get_user_model().objects.filter(username="unauthorized").exists())

    def test_anonymous_member_management_redirects_to_sign_in(self) -> None:
        response = self.client.get(reverse("households:members"))

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('households:members')}")
