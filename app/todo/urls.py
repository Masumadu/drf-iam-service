from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_all_todos, name="view_all_todos"),
    path("create/", views.create_todo, name="create_todo"),
    path("<uuid:todo_id>/detail/", views.get_todo, name="get_todo"),
    path("<uuid:todo_id>/update/", views.update_todo, name="update_todo"),
    path("<uuid:todo_id>/delete/", views.delete_todo, name="delete_todo"),
]
