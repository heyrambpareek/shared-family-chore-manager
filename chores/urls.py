from django.urls import path

from . import views


app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="list"),
    path("new/", views.chore_create, name="create"),
    path("<int:pk>/edit/", views.chore_edit, name="edit"),
    path("<int:pk>/delete/", views.chore_delete, name="delete"),
]
