from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from account.models import ProviderProfile
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="sub_categories")

    class Meta:
        ordering = ["slug"]
        indexes = [models.Index(fields=["slug"])]

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent and (self.parent == self):
            raise ValidationError("A category can not be its own parent")
        return super().clean()


def _validate_item_properties(value):
    for k, v in value.items():
        if not isinstance(v, list):
            raise ValidationError(
                "properties values must only be list of strings")
        if not all(isinstance(m, str) for m in v):
            raise ValidationError(
                "properties values must only be list of stringsdfsdf")


class Item(models.Model):
    class ItemSubmissionStatus(models.TextChoices):
        VERIFIED = 'VF', 'Verified'
        PENDING = 'PN', 'Verfication pending'
        DECLINED = 'DC', 'Declined'

    class ItemPriceCurrency(models.TextChoices):
        USD = 'USD', 'USA Dollar'
        IRR = 'IRR', 'Iranian Rial'

    name = models.CharField(max_length=250)
    slug = models.CharField(max_length=250, unique=True)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_items")
    properties = models.JSONField(validators=[_validate_item_properties])
    description = models.TextField()
    remaining_items = models.PositiveIntegerField(default=0, blank=False)
    price = models.DecimalField(
        default=0, blank=False, max_digits=12, decimal_places=2)
    currency = models.TextField(
        max_length=3, choices=ItemPriceCurrency, default=ItemPriceCurrency.IRR)
    created = models.DateTimeField(auto_now_add=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    submission_status = models.CharField(
        max_length=2, choices=ItemSubmissionStatus, default=ItemSubmissionStatus.PENDING)
    submission_review_message = models.TextField(
        null=True, default="", blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-publish", "slug"]
        indexes = [
            models.Index(fields=['-publish']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.submitted_by_id and self.provider.user.id != self.submitted_by_id:
            raise ValidationError(
                "item provider is not owned by you")
        return super().clean()

    def get_absolute_url(self):
        return reverse("items:item_details", kwargs={"pk": self.pk})
