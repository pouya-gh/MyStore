from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http.response import JsonResponse
from .forms import CustomerProfileForm, ProviderProfileForm, MyUserChangeForm
from .models import ProviderProfile, ProfileStatus
from items.models import Category, Item

from django.conf import settings

from django.core.management import call_command

import os
import json

@login_required
def populate_db_default_data(request):
    if request.user.username != "pouya" or Category.objects.count() != 0:# just a stupid check
        return JsonResponse({"msg": "no"})
    
    with open(settings.BASE_DIR / 'items_default_db_data.js') as f:
        contents = json.loads(f.read())
        for obj in contents:
            if obj["model"] == "items.category":
                Category.objects.create(name=obj["fields"]["name"],
                                        slug=obj["fields"]["slug"],
                                        parent_id=obj["fields"]["parent"])
            elif obj["model"] == "items.item":
                Item.objects.create(name=obj["fields"]["name"],
                                    slug=obj["fields"]["slug"],
                                    provider_id=obj["fields"]["provider"],
                                    submitted_by_id=obj["fields"]["submitted_by"],
                                    properties=json.dumps(obj["fields"]["properties"]),
                                    description=obj["fields"]["description"],
                                    remaining_items=obj["fields"]["remaining_items"],
                                    price=obj["fields"]["price"],
                                    category_id=obj["fields"]["category"])

    with open(settings.BASE_DIR / 'account_default_db_data.js') as f:
        contents = json.loads(f.read())
        for obj in contents:
            if obj["model"] == "account.providerprofile":
                ProviderProfile.objects.create(user_id=obj["fields"]["user"],
                                                official_name=obj["fields"]["official_name"],
                                                name=obj["fields"]["name"],
                                                social_code=obj["fields"]["social_code"],
                                                country=json.dumps(obj["fields"]["country"]),
                                                province=obj["fields"]["province"],
                                                city=obj["fields"]["city"],
                                                address=obj["fields"]["address"],
                                                phone_number=obj["fields"]["phone_number"],
                                                phone_number2=obj["fields"]["phone_number2"])
        # call_command('loaddata', 
        #              settings.BASE_DIR / 'account_default_db_data.js', 
        #              settings.BASE_DIR / 'items_default_db_data.js')


    return JsonResponse({"msg": "ok"})

def user_create(request):
    # auto creating super user as a workaround for render
    # because free render doesn't allow shell access
    if get_user_model().objects.filter(is_superuser=True).count() == 0:
        new_superuser = get_user_model().objects.create_superuser(
            username=settings.SUPERUSER_USERNAME,
            password=settings.SUPERUSER_PASSWORD
        )
        new_superuser.save()
    
    if request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()

            return redirect("home")
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
            return redirect("home")
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
        return redirect(reverse("account:my_provider_profiles_list"))


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
        return redirect(reverse("account:my_provider_profiles_list"))


class ProviderProfileDeleteView(ProviderProfileQuerySetMixin,
                                LoginRequiredMixin,
                                DeleteView):
    success_url = reverse_lazy("account:my_provider_profiles_list")
    template_name = 'account/providerprofile/confirm_delete.html'


@login_required
def get_current_user_provider_profiles(request):
    providers = request.user.providers_list.all()

    profile_list = []
    for p in providers:
        profile_list.append({"name": str(p), "id": str(p.id)})

    return JsonResponse({"providers_list": profile_list})
