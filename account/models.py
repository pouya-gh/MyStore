from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

class ProfileStatus(models.TextChoices):
    VERIFIED = 'VF', 'Verified'
    PENDING = 'PN', 'Verfication pending'
    DECLINED = 'DC', 'Declined'

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
                                on_delete=models.CASCADE, 
                                related_name='profile',
                                primary_key=True)
    social_code = models.CharField(max_length=10, unique=True)
    birth_date = models.DateField()
    country = CountryField()
    province = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=11)
    phone_number2 = models.CharField(max_length=11, null=True, blank=True)
    status = models.CharField(max_length=2, choices=ProfileStatus.choices, default=ProfileStatus.PENDING)

    class Meta:
        ordering = ["user", "social_code"]
        indexes = [
            models.Index(fields=['social_code']), 
            ]

    def __str__(self):
        return self.user.username


class ProviderProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='providers_list')
    official_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    social_code = models.CharField(max_length=10, unique=True)
    country = CountryField()
    province = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=11)
    phone_number2 = models.CharField(max_length=11, null=True, blank=True)
    status = models.CharField(max_length=2, choices=ProfileStatus.choices, default=ProfileStatus.PENDING)

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
