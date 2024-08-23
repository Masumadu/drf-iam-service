from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_all_accounts, name="view_all_accounts"),
    path("detail/", views.get_account, name="get_account"),
    path("create/", views.create_account, name="create_account"),
    path("verify/email/", views.verify_account_email, name="verify_account_email"),
    path(
        "verify/email/link/",
        views.resend_email_verification,
        name="resend_email_verification",
    ),
    path("apikey/", views.generate_apikey, name="generate_api_key"),
    path(
        "apikey/<str:apikey>/detail/",
        views.get_account_by_apikey,
        name="get_account_by_apikey",
    ),
    path(
        "apikey/toggle-status/", views.toggle_apikey_status, name="toggle_apikey_status"
    ),
    path("login/", views.login_account, name="login_account"),
    path("refresh-token/", views.refresh_access_token, name="refresh_access_token"),
    path(
        "password/reset/request/",
        views.reset_password_request,
        name="reset_password_request",
    ),
    path("password/reset/", views.reset_password, name="reset_password"),
    path("password/change/", views.change_password, name="change_password"),
    path("otp/", views.send_one_time_password, name="send_one_time_password"),
    path(
        "otp/confirm/",
        views.confirm_one_time_password,
        name="confirm_one_time_password",
    ),
    path("delete/", views.deactivate_account, name="deactivate_account"),
    path("group/", views.update_account_group, name="update_account_group"),
]
