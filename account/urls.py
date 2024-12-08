from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "account"
urlpatterns = [
    path("", view=views.index_temp, name='index_temp'),
    path("signup/", view=views.user_create, name="signup"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
]
