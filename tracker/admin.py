from django.contrib import admin

from .models import SiteVisitTracker

@admin.register(SiteVisitTracker)
class SiteVisitTrackerAdmin(admin.ModelAdmin):
    list_display = ["ip", "counter", "last_encounter", "location"]