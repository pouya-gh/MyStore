from django import test
from account.models import ProviderProfile
from django.core.exceptions import ValidationError
from ..models import Item, Category
from django.contrib.auth import get_user_model


class CategoryModelTests(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        Category.objects.create(name="Cat 1", slug="cat1")

    def test_category_to_string(self):
        cat = Category.objects.first()
        self.assertEqual(cat.name, str(cat))

    def test_a_category_cant_be_its_own_parent(self):
        cat = Category.objects.first()
        cat.parent = cat
        with self.assertRaises(ValidationError):
            cat.full_clean()

    def test_name_and_slug_max_length(self):
        cat = Category.objects.first()
        self.assertEqual(cat._meta.get_field('name').max_length, 100)
        self.assertEqual(cat._meta.get_field('slug').max_length, 100)
