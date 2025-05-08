from django.db import models

class SiteVisitTracker(models.Model):
    ip = models.GenericIPAddressField()
    counter = models.PositiveIntegerField(default=1)
    first_encounter = models.DateTimeField(auto_now_add=True)
    last_encounter = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=50, default="")

    class Meta:
        ordering = ["-last_encounter", "-first_encounter"]
        indexes = [
            models.Index(fields=["-last_encounter"])
        ]

    def __str__(self):
        return self.ip


class SiteVisitTrackerVisitedPath(models.Model):
    path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.ForeignKey(SiteVisitTracker, on_delete=models.CASCADE, related_name="visited_paths")

    class Meta:
        ordering = ['-updated_at', "ip"]
        indexes = [
            models.Index(fields=["ip"])
        ]