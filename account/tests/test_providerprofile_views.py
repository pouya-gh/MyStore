from django.test import TestCase
from ..models import ProviderProfile, ProfileStatus
from ..forms import ProviderProfileForm
from django.contrib.auth import get_user_model
from django.urls import reverse


class ProviderProfileCreateViewsTests(TestCase):
    valid_provider_form_data = {"official_name": "fname",
                                "name": "lname",
                                "social_code": "1111111111",
                                "country": "IR",
                                "province": "Tehran",
                                "city": "Tehran",
                                "address": "123 fake street",
                                "phone_number": "09875430512",
                                "phone_number2": "09875430555",
                                }

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user1 = user_model.objects.create_user(
            username="user1", password="user1user1")
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
        response = self.client.post(
            reverse("account:provider_profile_create"), data=self.valid_provider_form_data)
        final_profile_count = ProviderProfile.objects.all().count()
        self.assertRedirects(response, "/providerprofile/list")
        self.assertEqual(initial_profile_count, 0)
        self.assertEqual(final_profile_count, 1)

    def test_success_full_creation_works_sets_user_to_current_user(self):
        self.client.login(username="user1", password="user1user1")
        user = get_user_model().objects.all().filter(username="user1").first()
        response = self.client.post(
            reverse("account:provider_profile_create"), data=self.valid_provider_form_data)
        profile = ProviderProfile.objects.all().filter(
            social_code=self.valid_provider_form_data['social_code']).first()
        self.assertEqual(profile.user, user)


class ProviderProfileUpdateAndDeleteTests(TestCase):
    valid_provider_form_data = {"official_name": "fname",
                                "name": "lname",
                                "social_code": "1111111111",
                                "country": "IR",
                                "province": "Tehran",
                                "city": "Tehran",
                                "address": "123 fake street",
                                "phone_number": "09875430512",
                                "phone_number2": "09875430555",
                                }

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user1 = user_model.objects.create_user(
            username="user1", password="user1user1")
        user1.save()

        ProviderProfile.objects.create(
            **ProviderProfileUpdateAndDeleteTests.valid_provider_form_data, user=user1)

    def test_update_url_exits(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/providerprofile/1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/providerprofile/form.html")
        self.assertIsInstance(response.context['form'], ProviderProfileForm)

    def test_update_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(
            reverse("account:provider_profile_update", args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/providerprofile/form.html")
        self.assertIsInstance(response.context['form'], ProviderProfileForm)

    def test_update_url_works_only_when_logged_in(self):
        response = self.client.get(
            reverse("account:provider_profile_update", args=[1]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_update_loads_only_profiles_of_loggedin_user(self):
        user2 = get_user_model().objects.create_user(
            username="user2", password="user2user2")
        user2.save()
        self.client.login(username="user2", password="user2user2")
        response = self.client.get(
            reverse("account:provider_profile_update", args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_update_profile_works_with_valid_data(self):
        self.client.login(username="user1", password="user1user1")
        initial_phone_number = ProviderProfile.objects.filter(
            id=1).first().phone_number
        new_data = self.valid_provider_form_data.copy()
        new_data["phone_number"] = "09351111111"
        response = self.client.post(reverse("account:provider_profile_update", args=[1]),
                                    data=new_data)
        profile = ProviderProfile.objects.filter(id=1).first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(profile.phone_number, new_data["phone_number"])
        self.assertNotEqual(profile.phone_number, initial_phone_number)

    def test_successful_update_profile_sets_verfication_status_to_pending(self):
        self.client.login(username="user1", password="user1user1")
        new_data = self.valid_provider_form_data.copy()
        new_data["phone_number"] = "09351111111"
        response = self.client.post(reverse("account:provider_profile_update", args=[1]),
                                    data=new_data)
        profile = ProviderProfile.objects.filter(id=1).first()
        self.assertEqual(profile.status, ProfileStatus.PENDING)

    def test_deletion_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        new_data = self.valid_provider_form_data.copy()
        new_data['social_code'] = "2222222222"
        ProviderProfile.objects.create(**new_data, user_id=1)
        response = self.client.post("/providerprofile/delete/2")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProviderProfile.objects.all().count(), 1)

    def test_deletion_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        new_data = self.valid_provider_form_data.copy()
        new_data['social_code'] = "2222222222"
        ProviderProfile.objects.create(**new_data, user_id=1)
        response = self.client.post(
            reverse("account:provider_profile_delete", args=[2]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProviderProfile.objects.all().count(), 1)

    def test_profile_can_only_be_deleted_by_owner(self):
        user2 = get_user_model().objects.create_user(
            username="user2", password="user2user2")
        user2.save()
        self.client.login(username="user2", password="user2user2")
        response = self.client.post(
            reverse("account:provider_profile_delete", args=[1]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(ProviderProfile.objects.all().count(), 1)

    def test_deletion_only_works_if_signin(self):
        response = self.client.post(
            reverse("account:provider_profile_delete", args=[1]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))
