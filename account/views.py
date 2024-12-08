from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

def index_temp(request):
    return HttpResponse("hello!")

def user_create(request):
    if request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()

            return redirect("account:index_temp")
    else:
        form = UserCreationForm()
        
    return render(request, "registration/signup.html", {"form": form})
    