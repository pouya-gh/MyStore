from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

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
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class ProviderProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider')
    official_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    social_code = models.CharField(max_length=10, unique=True)
    country = CountryField()
    province = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=11)
    phone_number2 = models.CharField(max_length=11, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.official_name})"
        else:
            return self.official_name
