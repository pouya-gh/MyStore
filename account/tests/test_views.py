from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from datetime import date
from ..forms import MyUserChangeForm, CustomerProfileForm
from ..models import CustomerProfile


class SignupViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user1 = user_model.objects.create_user(
            username="user1", password="user1user1")
        user1.save()

    def test_signup_page_exists(self):
        response = self.client.get("/en/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_url_has_correct_name(self):
        response = self.client.get(reverse("account:signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_url_uses_correct_template(self):
        response = self.client.get(reverse("account:signup"))
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertIsInstance(response.context["form"], UserCreationForm)

    def test_signup_request_works_with_valid_data(self):
        signup_data = {"username": "user2",
                       "password1": "user2user2", "password2": "user2user2"}
        response = self.client.post(
            reverse("account:signup"), data=signup_data)
        
        user_count = get_user_model().objects.all().count()
        self.assertRedirects(response, "/en/")
        self.assertEqual(user_count, 3) # its 3 users now since i'm adding 1 super user in views if one doens't already exist.
        # this is because i'm using free render and i don't have access to terminal with free render account.


class UpdateUserViewTests(TestCase):
    valid_profile_form_data = {"first_name": "fname",
                               "last_name": "lname",
                               "email": "user1@mail.com",
                               "social_code": "1111111111",
                               "birth_date": date(1990, 10, 10),
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

    def test_page_exits_if_logged_in(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/en/profile/update")
        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_if_not_logged_in(self):
        response = self.client.get("/en/profile/update")
        self.assertTrue(response.url.startswith("/en/login"))

    def test_update_profile_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("account:cutomer_profile_set"))
        self.assertEqual(response.status_code, 200)

    def test_update_profile_uses_correct_template_with_get_request(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("account:cutomer_profile_set"))
        self.assertTemplateUsed(response, "account/customerprofile/form.html")
        self.assertIsInstance(response.context["form"], CustomerProfileForm)
        self.assertIsInstance(
            response.context["auth_user_form"], MyUserChangeForm)

    def test_update_profile_request_works_with_valid_data(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.post(
            reverse("account:cutomer_profile_set"), data=self.valid_profile_form_data)
        self.assertRedirects(response, "/en/")

    def test_successful_update_profile_request_creates_profile_if_it_doesnt_exist(self):
        self.client.login(username="user1", password="user1user1")
        initial_profile_count = CustomerProfile.objects.all().count()
        response = self.client.post(
            reverse("account:cutomer_profile_set"), data=self.valid_profile_form_data)
        final_profile_count = CustomerProfile.objects.all().count()
        self.assertEqual(initial_profile_count, 0)
        self.assertEqual(final_profile_count, 1)

    def test_update_profile_request_reloads_form_with_invalid_data(self):
        self.client.login(username="user1", password="user1user1")
        data = {"first_name": "fname",
                "last_name": "lname",
                "email": "user1@mail.com",
                "social_code": "",
                "birth_date": date(1990, 10, 10),
                "phone_number": "09875430512",
                "phone_number2": "09875430555",
                }
        response = self.client.post(
            reverse("account:cutomer_profile_set"), data=data)
        self.assertTemplateUsed(response, "account/customerprofile/form.html")
        self.assertIsInstance(response.context["form"], CustomerProfileForm)
        self.assertIsInstance(
            response.context["auth_user_form"], MyUserChangeForm)
