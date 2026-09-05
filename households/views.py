from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from .forms import MemberCreateForm
from .models import Membership


def home(request):
    if request.user.is_authenticated:
        return redirect("chores:list")
    return render(request, "home.html")


def adult_required(view):
    def wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "membership") or request.user.membership.role != Membership.Role.ADULT:
            return HttpResponseForbidden("Adult access is required.")
        return view(request, *args, **kwargs)

    return login_required(wrapped)


@adult_required
def member_list(request):
    membership = request.user.membership
    return render(
        request,
        "households/member_list.html",
        {"members": membership.household.memberships.select_related("user")},
    )


@adult_required
def member_create(request):
    form = MemberCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(household=request.user.membership.household)
        return redirect("households:members")
    return render(request, "households/member_form.html", {"form": form})
