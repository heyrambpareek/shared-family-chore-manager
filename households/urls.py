from django.urls import path

from . import views


app_name = "households"

urlpatterns = [
    path("members/", views.member_list, name="members"),
    path("members/add/", views.member_create, name="member-create"),
]
