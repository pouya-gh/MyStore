from django.contrib import admin

from .models import SiteVisitTracker, SiteVisitTrackerVisitedPath

@admin.register(SiteVisitTracker)
class SiteVisitTrackerAdmin(admin.ModelAdmin):
    list_display = ["ip", "counter", "last_encounter", "location"]


@admin.register(SiteVisitTrackerVisitedPath)
class SiteVIsitTrackerPathAdmin(admin.ModelAdmin):
    list_display = ["ip", "updated_at", "path"]
    list_filter = [("ip", admin.RelatedOnlyFieldListFilter), "path"]
    search_fields = ['ip', 'path']
