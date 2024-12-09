from django.contrib import admin
from . import models

@admin.register(models.CustomerProfile)
class CustormerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "social_code", "phone_number", "status"]
    list_filter = ["user", "status"]

@admin.register(models.ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ["official_name", "name", "user", "social_code", "phone_number", "status"]
    list_filter = ["user", "status"]