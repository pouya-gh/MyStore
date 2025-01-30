from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from account.models import ProviderProfile
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

import os


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
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


def is_alphnum_and_space(prop_name: str) -> bool:
    return prop_name.replace(" ", "").isalnum()


def _validate_item_properties(value):
    for k, v in value.items():
        if not is_alphnum_and_space(k):
            raise ValidationError(
                "property's keys must contain only alphanumeric characters and space")

        if not isinstance(v, str):
            raise ValidationError(
                "properties values must only be a string")


def _item_image_directory_path(instance, filename):
    return 'items/{0}/{1}'.format(instance.slug, filename)


class ItemQuerySet(models.QuerySet):
    def verified_items(self):
        return self.filter(submission_status="VF")

    def pending_items(self):
        return self.filter(submission_status="PN")

    def declined_items(self):
        return self.filter(submission_status="DC")


class Item(models.Model):
    class ItemSubmissionStatus(models.TextChoices):
        VERIFIED = 'VF', 'Verified'
        PENDING = 'PN', 'Verfication pending'
        DECLINED = 'DC', 'Declined'

    class ItemPriceCurrency(models.TextChoices):
        USD = 'USD', 'USA Dollar'
        IRR = 'IRR', 'Iranian Rial'

    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_items")
    properties = models.JSONField(validators=[_validate_item_properties])
    description = models.TextField()
    image = models.ImageField(upload_to=_item_image_directory_path, blank=True)
    remaining_items = models.PositiveIntegerField(default=0, blank=False)
    price = models.DecimalField(
        default=0, blank=False, max_digits=12, decimal_places=2)
    currency = models.TextField(
        max_length=3, choices=ItemPriceCurrency, default=ItemPriceCurrency.USD)
    created = models.DateTimeField(auto_now_add=True)
    publish = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    submission_status = models.CharField(
        max_length=2, choices=ItemSubmissionStatus, default=ItemSubmissionStatus.PENDING)
    submission_review_message = models.TextField(
        null=True, default="", blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)

    objects = ItemQuerySet.as_manager()

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

    def save(self, *args, **kwargs):
        """
        remove the old image if it was changed
        """
        if self.id:  # the item is being updated
            previous = Item.objects.get(pk=self.id)

            if previous.image and (previous.image != self.image):
                try:
                    os.remove(previous.image.path)
                except FileNotFoundError:  # this can happen if file was deleted manually and the db wasn't updated
                    print("Item image not found")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("items:item_details", kwargs={"pk": self.pk})

    def generate_sku(self):
        props = self.properties.items()
        props_sorted = sorted(props)
        sku = self.slug
        for _, v in props_sorted:
            sku += "-" + slugify(v.lower())
        return sku


class ShoppingCartItem(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE,
                                 related_name="shopping_cart_items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)
    properties = models.JSONField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    additional_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} {self.item}"

    def generate_sku(self):
        return self.item.generate_sku()
