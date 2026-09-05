from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_configured_user_model_can_be_created(self) -> None:
        user = get_user_model().objects.create_user(
            username="family-member", password="test-password"
        )

        self.assertEqual(user.username, "family-member")

    def test_home_page_is_available(self) -> None:
        response = self.client.get("/")

        self.assertContains(response, "Shared Family Chore Manager")

    def test_registration_creates_adult_household_membership(self) -> None:
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "adult",
                "email": "adult@example.com",
                "password1": "Strong-test-password-123",
                "password2": "Strong-test-password-123",
                "household_name": "The Testers",
                "timezone": "UTC",
            },
        )

        self.assertRedirects(response, reverse("chores:list"))
        user = get_user_model().objects.get(username="adult")
        self.assertEqual(user.membership.role, "adult")
        self.assertEqual(user.membership.household.name, "The Testers")

    def test_registration_rejects_an_invalid_household_timezone(self) -> None:
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "adult",
                "email": "adult@example.com",
                "password1": "Strong-test-password-123",
                "password2": "Strong-test-password-123",
                "household_name": "The Testers",
                "timezone": "Not/A-Timezone",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="adult").exists())

    def test_valid_credentials_sign_in_and_redirect_to_chores(self) -> None:
        user = get_user_model().objects.create_user("member", password="test-password")
        from households.models import Household, Membership

        household = Household.objects.create(name="Home", timezone="UTC")
        Membership.objects.create(household=household, user=user, role="adult")

        response = self.client.post(
            reverse("accounts:login"), {"username": "member", "password": "test-password"}
        )

        self.assertRedirects(response, reverse("chores:list"))
