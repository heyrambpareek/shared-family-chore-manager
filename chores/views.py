from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from households.models import Membership

from .forms import ChoreSeriesForm, create_initial_occurrence
from .models import ChoreSeries


def adult_required(view):
    def wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "membership") or request.user.membership.role != Membership.Role.ADULT:
            return HttpResponseForbidden("Adult access is required.")
        return view(request, *args, **kwargs)

    return login_required(wrapped)


def series_for_adult(request, pk):
    return get_object_or_404(
        ChoreSeries,
        pk=pk,
        household=request.user.membership.household,
        is_active=True,
    )


@login_required
def chore_list(request):
    membership = request.user.membership
    if membership.role == Membership.Role.ADULT:
        series = ChoreSeries.objects.filter(household=membership.household, is_active=True).select_related("assignee__user")
    else:
        series = ChoreSeries.objects.filter(household=membership.household, assignee=membership, is_active=True)
    return render(request, "chores/list.html", {"series": series, "is_adult": membership.role == Membership.Role.ADULT})


@adult_required
def chore_create(request):
    form = ChoreSeriesForm(request.POST or None, household=request.user.membership.household)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            series = form.save()
            create_initial_occurrence(series)
        return redirect("chores:list")
    return render(request, "chores/form.html", {"form": form, "heading": "Create chore"})


@adult_required
def chore_edit(request, pk):
    series = series_for_adult(request, pk)
    form = ChoreSeriesForm(request.POST or None, instance=series, household=request.user.membership.household)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            series = form.save()
            series.occurrences.all().delete()
            create_initial_occurrence(series)
        return redirect("chores:list")
    return render(request, "chores/form.html", {"form": form, "heading": "Edit chore"})


@adult_required
def chore_delete(request, pk):
    series = series_for_adult(request, pk)
    if request.method == "POST":
        series.is_active = False
        series.save(update_fields=["is_active"])
        return redirect("chores:list")
    return render(request, "chores/confirm_delete.html", {"series": series})
