from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def validate_timezone(value: str) -> None:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValidationError("Enter a valid IANA timezone, such as Europe/London.") from exc


class Household(models.Model):
    name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=64, default="UTC", validators=[validate_timezone])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Membership(models.Model):
    class Role(models.TextChoices):
        ADULT = "adult", "Adult"
        CHILD = "child", "Child"

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="memberships")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership")
    role = models.CharField(max_length=5, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return f"{self.user} in {self.household}"
