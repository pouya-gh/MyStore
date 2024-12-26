from django.test import TestCase
from account.models import ProviderProfile, ProfileStatus
from ..models import Item
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone


class ItemModelTests(TestCase):
    valid_item_data = {"name": "Shoes",
                       "slug": "shoes",
                       "properties": {"size": ["8", "9"], "color": ["white", "color"], },
                       "description": "a pair of very good shoes",
                       "remaining_items": 100}

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="user1", password="user1user1")
        user.save()
        provider = ProviderProfile.objects.create(user=user,
                                                  official_name="official name",
                                                  social_code="1234567890",
                                                  country="IR",
                                                  province="province",
                                                  city="city",
                                                  address="123 fake street",
                                                  phone_number="09345786523",
                                                  phone_number2="09345786222",)
        Item.objects.create(submitted_by=user,
                            provider=provider,
                            **ItemModelTests.valid_item_data)

    def test_item_is_created_with_valid_data(self):
        user = get_user_model().objects.first()
        provider = ProviderProfile.objects.first()
        self.assertEqual(Item.objects.count(), 1)
        data = self.valid_item_data.copy()
        data['slug'] = 'shoes2'
        Item.objects.create(submitted_by=user,
                            provider=provider,
                            **data)
        self.assertEqual(Item.objects.count(), 2)

    def test_item_status_is_pending_by_default(self):
        item = Item.objects.first()
        self.assertEqual(item.submission_status,
                         Item.ItemSubmissionStatus.PENDING)

    def test_name_and_slug_length(self):
        item = Item.objects.first()
        name_field = item._meta.get_field("name")
        slug_field = item._meta.get_field("slug")
        self.assertEqual(name_field.max_length, 250, "name field wrong length")
        self.assertEqual(slug_field.max_length, 250, "slug field wrong length")

    def test_created_field_get_auto_added(self):
        item = Item.objects.first()

        self.assertIsNotNone(item.created)
        self.assertIsNotNone(item.publish)
        self.assertIsNotNone(item.updated)

    def test_publish_date_field_default_is_now(self):
        item = Item.objects.first()

        self.assertEqual(item._meta.get_field("publish").default, timezone.now)

    def test_updated_field_gets_set_automatically_on_item_update(self):
        item = Item.objects.first()
        previous_value = item.updated
        item.description = "new description"
        item.save()
        new_value = item.updated
        self.assertNotEqual(previous_value, new_value)

    def test_item_name(self):
        item = Item.objects.first()

        self.assertEqual(str(item), item.name)

    def test_item_properties_validator(self):
        item = Item.objects.first()
        item.properties = {"p1": "v1"}
        with self.assertRaises(ValidationError):
            item.full_clean()
        item.properties = {"p1": [1]}
        with self.assertRaises(ValidationError):
            item.full_clean()
        item.properties = {"p1": {}}
        with self.assertRaises(ValidationError):
            item.full_clean()

        item.properties = {"p1": ["v1"]}
        item.full_clean()

    def test_item_provider_is_owned_by_submitter(self):
        user2 = get_user_model().objects.create_user(
            username="user2", password="user1user2")
        provider = ProviderProfile.objects.first()
        data = self.valid_item_data.copy()
        data['slug'] = 'shoes2'
        item = Item.objects.create(submitted_by=user2,
                                   provider=provider,
                                   **data)
        with self.assertRaises(ValidationError):
            item.full_clean()
