from django.test import TestCase
from ..models import ProviderProfile, ProfileStatus
from django.contrib.auth import get_user_model
from django.db import IntegrityError

class ProviderProfileTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create(username="user1", password="user1user1")
        ProviderProfile.objects.create(user=self.user,
                                       official_name="official name",
                                       social_code="1234567890",
                                       country="IR",
                                       province="province",
                                       city="city",
                                       address="123 fake street",
                                       phone_number="09345786523",
                                       phone_number2="09345786222",)
        
        
    def test_provider_profile_exists(self):
        number_of_profiles = ProviderProfile.objects.all().count()

        self.assertEqual(number_of_profiles, 1)


    def test_provider_profile_status_defaults_to_pending(self):
        profile = ProviderProfile.objects.all().first()

        self.assertEqual(profile.status, ProfileStatus.PENDING)


    def test_cant_create_provider_profile_without_social_code(self):
        with self.assertRaises(IntegrityError):
            ProviderProfile.objects.create(user=self.user,
                                       official_name="official name",
                                       country="IR",
                                       province="province",
                                       city="city",
                                       address="123 fake street",
                                       phone_number="09345786523",
                                       phone_number2="09345786222",)
            

    def test_provider_profile_to_string_conversion(self):
        profile1 = ProviderProfile.objects.all().first()
        profile2 = ProviderProfile.objects.create(user=self.user,
                                       official_name="profile1 llc",
                                       name="name",
                                       social_code="1111111111",
                                       country="IR",
                                       province="province",
                                       city="city",
                                       address="456 fake street",
                                       phone_number="09345786111",
                                       phone_number2="09345786222",)
        
        self.assertEqual(str(profile1), profile1.official_name)
        self.assertEqual(str(profile2), f"{profile2.name} ({profile2.official_name})")

    
    def test_provider_profile_social_code_is_unique(self):
        profile1 = ProviderProfile.objects.all().first()
        with self.assertRaises(IntegrityError):
            ProviderProfile.objects.create(user=self.user,
                                        official_name="some name",
                                        social_code=profile1.social_code,
                                        country="IR",
                                        province="province",
                                        city="city",
                                        address="123 fake street",
                                        phone_number="09345786523",
                                        phone_number2="09345786222",)
            
    def test_provider_profile_phone_number2_can_be_null(self):
        ProviderProfile.objects.create(user=self.user,
                                    official_name="some name",
                                    social_code="1111111111",
                                    country="IR",
                                    province="province",
                                    city="city",
                                    address="123 fake street",
                                    phone_number="09345786523",)
        
        count = ProviderProfile.objects.all().count()

        self.assertEqual(count, 2)