from django import forms
from django.contrib.auth.forms import UserCreationForm

from households.models import Household, Membership

from .models import User


class RegistrationForm(UserCreationForm):
    household_name = forms.CharField(max_length=100)
    timezone = forms.CharField(max_length=64, initial="UTC")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "household_name", "timezone")

    def clean_timezone(self) -> str:
        timezone = self.cleaned_data["timezone"]
        field = Household._meta.get_field("timezone")
        field.run_validators(timezone)
        return timezone

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=commit)
        if commit:
            household = Household.objects.create(
                name=self.cleaned_data["household_name"],
                timezone=self.cleaned_data["timezone"],
            )
            Membership.objects.create(
                household=household, user=user, role=Membership.Role.ADULT
            )
        return user
