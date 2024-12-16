from django.db import models
from django.core.exceptions import ValidationError
from account.models import ProviderProfile
from django.conf import settings
from django.utils import timezone

def _validate_item_properties(value):
        for k, v in value.items():
            if not isinstance(v,list):
                raise ValidationError("properties values must only be list of strings")
            if not all(isinstance(m, str) for m in v):
                    raise ValidationError("properties values must only be list of stringsdfsdf")

class Item(models.Model):
    class ItemSubmissionStatus(models.TextChoices):
        VERIFIED = 'VF', 'Verified'
        PENDING = 'PN', 'Verfication pending'
        DECLINED = 'DC', 'Declined'

    name = models.CharField(max_length=250)
    slug = models.CharField(max_length=250, unique=True)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_items")
    properties = models.JSONField(validators=[_validate_item_properties])
    description = models.TextField()
    remaining_items = models.PositiveIntegerField(default=0, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    submission_status = models.CharField(max_length=2, choices=ItemSubmissionStatus, default=ItemSubmissionStatus.PENDING)
    submission_review_message = models.TextField(null=True, default="", blank=True)

    class Meta:
        ordering = ["-publish", "slug"]
        indexes = [
            models.Index(fields=['-publish']),
             models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name
    
    def clean(self):
         if self.provider.user != self.submitted_by:
             raise ValidationError("provider of the item must be owned by submitter of the item. item provider is not owned but submitted_by user")
         return super().clean()