from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Membership


class MemberCreateForm(UserCreationForm):
    role = forms.ChoiceField(choices=Membership.Role.choices)
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "role")

    def save(self, household, commit: bool = True):
        user = super().save(commit=commit)
        if commit:
            Membership.objects.create(
                household=household, user=user, role=self.cleaned_data["role"]
            )
        return user
