from django.urls import include, path

urlpatterns = [
    path("user/", include("app.user.urls")),
    path("todo/", include("app.todo.urls")),
]
