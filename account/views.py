from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from .forms import CustomerProfileForm, ProviderProfileForm

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
def user_profile_create(request):
    user = request.user
    
    if request.POST:
        try:
            form = CustomerProfileForm(request.POST, instance=user.profile)
        except ObjectDoesNotExist:
            form = CustomerProfileForm(request.POST)
            

        if form.is_valid():
            cd = form.cleaned_data
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
        
    return render(request, "account/customerprofile/form.html", {"form": form})


@login_required
def provider_profile_create(request):
    user = request.user
    
    if request.POST:
        form = ProviderProfileForm(request.POST) 

        if form.is_valid():
            cd = form.cleaned_data
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect("account:index_temp")
    else:
        form = ProviderProfileForm()
        
    return render(request, "account/providerprofile/form.html", {"form": form})
    