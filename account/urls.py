from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "account"
urlpatterns = [
    path("", view=views.index_temp, name='index_temp'),
    path("signup/", view=views.user_create, name="signup"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("profile/update", view=views.user_profile_create, name='cutomer_profile_set'),
    path("providerprofile/create", view=views.provider_profile_create, name='provider_profile_create'),
    path("providerprofile/list", view=views.ProviderProfileListview.as_view(), name='provider_profiles_list'),
]
