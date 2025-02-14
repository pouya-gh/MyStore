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