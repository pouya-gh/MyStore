from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "account"
urlpatterns = [
    path("signup/", view=views.user_create, name="signup"),
    path("login/", view=LoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("profile/update", view=views.user_profile_update,
         name='cutomer_profile_set'),
    path("providerprofile/create", view=views.ProviderProfileCreateView.as_view(),
         name='provider_profile_create'),
    path("myproviderprofiles", view=views.ProviderProfileListview.as_view(),
         name='my_provider_profiles_list'),
    path("current_user_provider_profiles.json", view=views.get_current_user_provider_profiles,
         name='current_user_provider_profiles_json'),
    path("providerprofile/<pk>", view=views.ProviderProfileUpdateView.as_view(),
         name='provider_profile_update'),
    path("providerprofile/delete/<pk>",
         view=views.ProviderProfileDeleteView.as_view(), name='provider_profile_delete'),
]
