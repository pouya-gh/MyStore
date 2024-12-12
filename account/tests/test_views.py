from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user_model.objects.create(username="user1", password="user1user1")


    def test_signup_page_exists(self):
        response = self.client.get("/signup/")
        self.assertEqual(response.status_code, 200)


    def test_signup_url_has_correct_name(self):
        response = self.client.get(reverse("account:signup"))
        self.assertEqual(response.status_code, 200)


    def test_signup_url_uses_correct_template(self):
        response = self.client.get(reverse("account:signup"))
        self.assertTemplateUsed(response, "registration/signup.html")
        self.assertIn("form", response.context)

    def test_signup_request_works_with_valid_data(self):
        signup_data = {"username":"user2", "password1":"user2user2", "password2":"user2user2"}
        response = self.client.post(reverse("account:signup"), data=signup_data)
        user_count = get_user_model().objects.all().count()
        self.assertRedirects(response, "/")
        self.assertEqual(user_count, 2)