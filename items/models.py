from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from account.models import ProviderProfile
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

import os


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    parent = models.ForeignKey("self",
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               related_name="sub_categories",
                               verbose_name=_("parent"))

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
                _("property's keys must contain only alphanumeric characters and space"))

        if not isinstance(v, str):
            raise ValidationError(
                _("properties values must only be a string"))


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
        VERIFIED = 'VF', _('Verified')
        PENDING = 'PN', _('Verfication pending')
        DECLINED = 'DC', _('Declined')

    class ItemPriceCurrency(models.TextChoices):
        USD = 'USD', _('USA Dollar')
        IRR = 'IRR', _('Iranian Rial')

    name = models.CharField(max_length=250, verbose_name=_("name"))
    slug = models.SlugField(max_length=250, unique=True, verbose_name=_("slug"))
    provider = models.ForeignKey(ProviderProfile,
                                 on_delete=models.CASCADE,
                                 verbose_name=_("provider"))
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE,
                                     related_name="submitted_items",
                                     verbose_name=_("submitted by"))
    properties = models.JSONField(validators=[_validate_item_properties], verbose_name=_("properties"))
    description = models.TextField(verbose_name=_("description"))
    image = models.ImageField(upload_to=_item_image_directory_path, blank=True, verbose_name=_("image"))
    remaining_items = models.PositiveIntegerField(default=0, blank=False, verbose_name=_("remaining items"))
    price = models.DecimalField(
        default=0, blank=False, max_digits=12, decimal_places=2, verbose_name=_("price"))
    currency = models.TextField(max_length=3,
                                choices=ItemPriceCurrency,
                                default=ItemPriceCurrency.USD,
                                verbose_name=_("currency"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
    publish = models.DateTimeField(default=timezone.now, verbose_name=_("publish"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("updated"))
    submission_status = models.CharField(max_length=2,
                                         choices=ItemSubmissionStatus,
                                         default=ItemSubmissionStatus.PENDING,
                                         verbose_name=_("submission status"))
    submission_review_message = models.TextField(
        null=True, default="", blank=True, verbose_name=_("submission review message"))

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("category"))

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
            raise ValidationError(_("item provider is not owned by you"))
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
                                 related_name="shopping_cart_items",
                                 verbose_name=_("customer"))
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name=_("item"))
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name=_("quantity"))
    properties = models.JSONField(verbose_name=_("properties"))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_("date added"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_("date updated"))
    additional_info = models.TextField(null=True, blank=True, verbose_name=_("additional info"))

    def __str__(self):
        return f"{self.quantity} {self.item}"

    def generate_sku(self):
        return self.item.generate_sku()
