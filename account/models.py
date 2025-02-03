from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _


class ProfileStatus(models.TextChoices):
    VERIFIED = 'VF', _('Verified')
    PENDING = 'PN', _('Verfication pending')
    DECLINED = 'DC', _('Declined')


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile',
                                primary_key=True,
                                verbose_name=_("User"))
    social_code = models.CharField(max_length=10,
                                   unique=True,
                                   blank=False,
                                   null=False,
                                   default=None,
                                   verbose_name=_("Social Code"))
    birth_date = models.DateField(verbose_name=_("Birth date"))
    country = CountryField(verbose_name=_("country"))
    province = models.CharField(max_length=200, verbose_name=_("province"))
    city = models.CharField(max_length=100, verbose_name=_("city"))
    address = models.CharField(max_length=300, verbose_name=_("address"))
    phone_number = models.CharField(
        max_length=11, verbose_name=_("phone number"))
    phone_number2 = models.CharField(
        max_length=11, null=True, blank=True, verbose_name=_("phone number 2"))
    status = models.CharField(
        max_length=2, choices=ProfileStatus.choices, default=ProfileStatus.PENDING, verbose_name=_("status"))

    class Meta:
        ordering = ["user", "social_code"]
        indexes = [
            models.Index(fields=['social_code']),
        ]

    def __str__(self):
        return self.user.username


class ProviderProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='providers_list', verbose_name=_("user"))
    official_name = models.CharField(
        max_length=100, verbose_name=_("official name"))
    name = models.CharField(max_length=100, null=True,
                            blank=True, verbose_name=_("provider name"))
    social_code = models.CharField(max_length=10,
                                   unique=True,
                                   blank=False,
                                   null=False,
                                   default=None,
                                   verbose_name=_("social code"))
    country = CountryField(verbose_name=_("country"))
    province = models.CharField(max_length=200, verbose_name=_("province"))
    city = models.CharField(max_length=100, verbose_name=_("city"))
    address = models.CharField(max_length=300, verbose_name=_("address"))
    phone_number = models.CharField(
        max_length=11, verbose_name=_("phone number"))
    phone_number2 = models.CharField(
        max_length=11, null=True, blank=True, verbose_name=_("phone number 2"))
    status = models.CharField(
        max_length=2, choices=ProfileStatus.choices, default=ProfileStatus.PENDING, verbose_name=_("status"))

    class Meta:
        ordering = ["user", "official_name"]
        indexes = [
            models.Index(fields=['social_code']),
            models.Index(fields=['official_name']),
        ]

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.official_name})"
        else:
            return self.official_name
