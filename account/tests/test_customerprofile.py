from django.test import TestCase
from ..models import CustomerProfile, ProfileStatus
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import date


class CustomerProfileTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create(
            username="user1", password="user1user1")
        self.user2 = user_model.objects.create(
            username="user2", password="user2user2")
        self.profile = CustomerProfile.objects.create(user=self.user,
                                                      social_code="1234567890",
                                                      birth_date=date(
                                                          1990, 1, 1),
                                                      country="IR",
                                                      province="province",
                                                      city="city",
                                                      address="123 fake street",
                                                      phone_number="09345786523",
                                                      phone_number2="09345786222",)

    def test_customer_profile_is_created_with_valid_data(self):
        number_of_profiles = CustomerProfile.objects.all().count()

        self.assertEqual(number_of_profiles, 1)

    def test_customer_profile_status_defaults_to_pending(self):
        self.assertEqual(self.profile.status, ProfileStatus.PENDING)

    def test_cant_create_customer_profile_withouth_social_code(self):
        with self.assertRaises(IntegrityError):
            CustomerProfile.objects.create(user=self.user2,
                                           birth_date=date(1990, 1, 1),
                                           country="IR",
                                           province="province",
                                           city="city",
                                           address="123 fake street",
                                           phone_number="09345786523",
                                           phone_number2="09345786222",)

    def test_customer_profile_to_string_conversion(self):
        self.assertEqual(str(self.profile), self.user.username)

    def test_customer_profile_social_code_is_unique(self):
        with self.assertRaises(IntegrityError):
            CustomerProfile.objects.create(user=self.user2,
                                           social_code="1234567890",  # <
                                           birth_date=date(1990, 1, 1),
                                           country="IR",
                                           province="province",
                                           city="city",
                                           address="123 fake street",
                                           phone_number="09345786523",
                                           phone_number2="09345786222",)

    def test_customer_profile_phone_number2_can_be_null(self):
        CustomerProfile.objects.create(user=self.user2,
                                       social_code="1111111111",
                                       birth_date=date(1990, 1, 1),
                                       country="IR",
                                       province="province",
                                       city="city",
                                       address="123 fake street",
                                       phone_number="09345786523",)

        count = CustomerProfile.objects.all().count()

        self.assertEqual(count, 2)

    def test_each_user_can_only_have_one_customer_profile(self):
        with self.assertRaises(IntegrityError):
            CustomerProfile.objects.create(user=self.user,  # <
                                           social_code="1111111111",
                                           birth_date=date(1990, 1, 1),
                                           country="IR",
                                           province="province",
                                           city="city",
                                           address="123 fake street",
                                           phone_number="09345786523",
                                           phone_number2="09345786222",)
