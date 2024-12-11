from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomerProfileForm, ProviderProfileForm, MyUserChangeForm
from .models import ProviderProfile, ProfileStatus


def index_temp(request):
    return render(request, "account/index_temp.html")


def user_create(request):
    if request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.save(commit=False)

            return redirect("account:index_temp")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def user_profile_update(request):
    user = request.user

    if request.POST:
        try:
            form = CustomerProfileForm(request.POST, instance=user.profile)
        except ObjectDoesNotExist:
            form = CustomerProfileForm(request.POST)
        auth_user_form = MyUserChangeForm(request.POST, instance=user)

        if form.is_valid() and auth_user_form.is_valid():
            cd = form.cleaned_data
            cd2 = auth_user_form.cleaned_data
            auth_user_form.save()
            profile = form.save(commit=False)
            if not profile.user_id:
                profile.user = user
            profile.save()
            return redirect("account:index_temp")
    else:
        try:
            form = CustomerProfileForm(instance=user.profile)
        except ObjectDoesNotExist:
            form = CustomerProfileForm()
        auth_user_form = MyUserChangeForm(instance=user)

    return render(request, "account/customerprofile/form.html",
                  {"form": form, "auth_user_form": auth_user_form})


class ProviderProfileQuerySetMixin:
    model = ProviderProfile

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(user=user)


class ProviderProfileCreateView(ProviderProfileQuerySetMixin,
                                LoginRequiredMixin,
                                CreateView):
    form_class = ProviderProfileForm
    template_name = "account/providerprofile/form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return redirect(reverse("account:provider_profiles_list"))


class ProviderProfileListview(ProviderProfileQuerySetMixin,
                              LoginRequiredMixin,
                              ListView):
    context_object_name = 'profiles'
    template_name = "account/providerprofile/list.html"


class ProviderProfileUpdateView(ProviderProfileQuerySetMixin,
                                LoginRequiredMixin,
                                UpdateView):
    form_class = ProviderProfileForm
    template_name = "account/providerprofile/form.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.status = ProfileStatus.PENDING
        self.object.save()
        return redirect(reverse("account:provider_profiles_list"))


class ProviderProfileDeleteView(ProviderProfileQuerySetMixin,
                                LoginRequiredMixin,
                                DeleteView):
    success_url = reverse_lazy("account:provider_profiles_list")
