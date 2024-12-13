from django.test import TestCase
from ..models import ProviderProfile
from ..forms import ProviderProfileForm
from django.contrib.auth import get_user_model
from django.urls import reverse

class ProviderProfileCreateViewsTests(TestCase):
    valid_provider_form_data = {"official_name":"fname",
                                "name":"lname",
                                "social_code":"1111111111",
                                "country":"IR",
                                "province":"Tehran",
                                "city":"Tehran",
                                "address":"123 fake street",
                                "phone_number":"09875430512",
                                "phone_number2":"09875430555",
                                }

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user1 = user_model.objects.create_user(username="user1", password="user1user1")
        user1.save()

    def test_creation_form_url_redirects_when_signedout(self):
        response = self.client.get("/providerprofile/create")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_creation_form_url_loads_when_signedin(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/providerprofile/create")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/providerprofile/form.html")
        self.assertIsInstance(response.context["form"], ProviderProfileForm)

    def test_creation_form_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("account:provider_profile_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/providerprofile/form.html")

    def test_creation_works_with_valid_data(self):
        self.client.login(username="user1", password="user1user1")
        initial_profile_count = ProviderProfile.objects.all().count()
        response = self.client.post(reverse("account:provider_profile_create"), data=self.valid_provider_form_data)
        final_profile_count = ProviderProfile.objects.all().count()
        self.assertRedirects(response, "/providerprofile/list")
        self.assertEqual(initial_profile_count, 0)
        self.assertEqual(final_profile_count, 1)