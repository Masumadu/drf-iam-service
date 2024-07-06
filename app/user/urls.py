from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_all_users, name="view_all_users"),
    path("create/", views.create_user, name="create_user"),
    path("detail/", views.get_user, name="get_user"),
    path("update/", views.update_user, name="update_user"),
    path("delete/", views.delete_user, name="delete_user"),
    path("login/", views.login_user, name="login_user"),
    path("refresh-token/", views.refresh_user_token, name="refresh_user_token"),
    path("change-password/", views.change_user_password, name="change_user_password"),
]
