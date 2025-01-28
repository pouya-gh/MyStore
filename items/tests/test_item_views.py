from django import test
from ..models import Item, Category, ShoppingCartItem
from ..forms import ItemForm
from account.models import ProviderProfile
from django.urls import reverse
from django.contrib.auth import get_user_model

import json


class ItemViewsTestMixin:
    valid_item_data = {"name": "Shoes",
                       "slug": "shoes",
                       "properties": {"size": "8", "color": "white"},
                       "description": "a pair of very good shoes",
                       "remaining_items": 100,
                       'image': '',
                       "price": 10.00}

    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user1 = user_model.objects.create_user(
            username="user1", password="user1user1")
        user1.save()
        user2 = user_model.objects.create_user(
            username="user2", password="user2user2")
        user2.save()

        provider1 = ProviderProfile.objects.create(user=user1,
                                                   official_name="official name",
                                                   social_code="1234567890",
                                                   country="IR",
                                                   province="province",
                                                   city="city",
                                                   address="123 fake street",
                                                   phone_number="09345786523",
                                                   phone_number2="09345786222",)

        ProviderProfile.objects.create(user=user2,
                                       official_name="official name2",
                                       social_code="1111111111",
                                       country="IR",
                                       province="province",
                                       city="city",
                                       address="123 fake street",
                                       phone_number="09345786523",
                                       phone_number2="09345786222",)

        category = Category.objects.create(name="Cat 1",
                                           slug="cat1")
        Category.objects.create(name="Cat 2",
                                slug="cat2")

        Item.objects.create(submitted_by=user1,
                            provider=provider1,
                            category=category,
                            submission_status="VF",
                            **ItemViewsTestMixin.valid_item_data)
        
        new_data = ItemViewsTestMixin.valid_item_data.copy()
        new_data["slug"] += "2"
        Item.objects.create(submitted_by=user1,
                            provider=provider1,
                            category=category,
                            **new_data)


class ItemListViewTests(ItemViewsTestMixin,
                        test.TestCase):

    def test_list_url_exits_and_only_loads_verified_items(self):
        response = self.client.get("/items/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 1)

    def test_list_view_has_correct_name_only_loads_verified_items(self):
        response = self.client.get(reverse("items:items_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 1)

    def test_list_filter_with_category(self):
        cat1 = Category.objects.get(slug="cat1")
        cat2 = Category.objects.get(slug="cat2")
        data = ItemViewsTestMixin.valid_item_data.copy()
        data["slug"] = "my-new-item"
        item2 = Item.objects.create(submitted_by_id=1,
                                    provider_id=1,
                                    category=cat2,
                                    **data)

        response = self.client.get(
            reverse("items:items_list") + f"?cat={cat1.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 1)
        self.assertNotEqual(items[0].slug, item2.slug)

    def test_homepage_is_items_list(self):
        url = reverse("home")
        self.assertEqual(url, "/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 1)


class ItemDetailViewTests(ItemViewsTestMixin,
                          test.TestCase):
    def test_detail_url_exits(self):
        response = self.client.get("/items/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("item", response.context)
        self.assertTemplateUsed(response, "items/item/detail.html")

    def test_detail_url_has_correct_name(self):
        response = self.client.get(
            reverse("items:item_details", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("item", response.context)
        self.assertTemplateUsed(response, "items/item/detail.html")

    def test_detail_view_has_add_to_cart_form_if_item_not_in_cart_and_is_logged_in(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(
            reverse("items:item_details", kwargs={"pk": 1}))
        self.assertEqual(ShoppingCartItem.objects.count(), 0)
        self.assertIn("shopping_cart_form", response.context)


class ItemCreateViewTests(ItemViewsTestMixin,
                          test.TestCase):
    def test_create_view_exits(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/items/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertTemplateUsed(response, "items/item/form.html")

    def test_create_view_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("items:item_create"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertTemplateUsed(response, "items/item/form.html")

    def test_create_view_works_only_signed_in(self):
        response = self.client.get(reverse("items:item_create"))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "items/item/form.html")

    def test_create_view_works_with_valid_data(self):
        self.client.login(username="user1", password="user1user1")
        self.assertEqual(Item.objects.count(), 2)
        data = ItemViewsTestMixin.valid_item_data.copy()
        data['name'] = "New Item"
        data['slug'] = "newitem"
        data['provider'] = 1
        data['category'] = 1
        data['properties'] = json.dumps(data['properties'])
        response = self.client.post(reverse("items:item_create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Item.objects.count(), 3)

    def test_create_view_doesnt_work_with_duplicate_slug(self):
        self.client.login(username="user1", password="user1user1")
        self.assertEqual(Item.objects.count(), 2)
        data = ItemViewsTestMixin.valid_item_data.copy()
        data['name'] = "New Item"
        data['provider'] = 1
        response = self.client.post(reverse("items:item_create"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Item.objects.count(), 2)

    def test_create_view_doesnt_work_if_current_user_doesnt_own_the_provider(self):
        self.client.login(username="user1", password="user1user1")
        self.assertEqual(Item.objects.count(), 2)
        data = ItemViewsTestMixin.valid_item_data.copy()
        data['slug'] = data['slug'] + "new"
        data['provider'] = 2
        response = self.client.post(reverse("items:item_create"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Item.objects.count(), 2)


class ItemUpdateViewTests(ItemViewsTestMixin,
                          test.TestCase):

    def test_update_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/items/update/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertTemplateUsed(response, "items/item/form.html")

    def test_update_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(
            reverse("items:item_update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertTemplateUsed(response, "items/item/form.html")

    def test_update_url_doesnt_work_if_not_loggedin(self):
        response = self.client.get(
            reverse("items:item_update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, "items/item/form.html")

    def test_update_only_works_if_user_owns_item(self):
        self.client.login(username="user2", password="user2user2")
        response = self.client.get(
            reverse("items:item_update", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed(response, "items/item/form.html")

    def test_update_url_works_with_valid_data(self):
        self.client.login(username="user1", password="user1user1")
        item = Item.objects.first()
        prev_description = item.description

        data = ItemViewsTestMixin.valid_item_data.copy()
        data["description"] = prev_description + "lorem ipsum"
        data["provider"] = 1
        data['properties'] = json.dumps(data['properties'])
        data['image'] = ''
        response = self.client.post(reverse("items:item_update", kwargs={"pk": 1}),
                                    data=data)
        new_description = Item.objects.first().description
        self.assertEqual(response.status_code, 302)
        self.assertEqual(new_description, prev_description + "lorem ipsum")


class ItemDeleteViewTests(ItemViewsTestMixin,
                          test.TestCase):
    def test_delete_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/items/delete/1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "items/item/confirm_delete.html")

    def test_delete_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(
            reverse("items:item_delete", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "items/item/confirm_delete.html")

    def test_delete_url_doesnt_work_if_not_loggedin(self):
        response = self.client.get(
            reverse("items:item_delete", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_delete_only_works_if_current_user_doesnt_own_it(self):
        self.client.login(username="user2", password="user2user2")
        response = self.client.get(
            reverse("items:item_delete", kwargs={"pk": 2})
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_works(self):
        self.client.login(username="user1", password="user1user1")
        user = get_user_model().objects.first()
        provider = ProviderProfile.objects.first()
        data = ItemViewsTestMixin.valid_item_data.copy()
        data['slug'] = "item3"
        new_item = Item.objects.create(submitted_by=user,
                                       provider=provider,
                                       **data)
        old_count = Item.objects.count()
        response = self.client.post(
            reverse("items:item_delete", kwargs={"pk": new_item.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(old_count, Item.objects.count())


class CurrentUserItemListViewTests(ItemViewsTestMixin,
                                   test.TestCase):

    def test_current_user_item_list_url_exits(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/items/myitems")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 2)

    def test_current_user_item_list_view_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("items:current_user_items"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 2)

    def test_current_user_item_list_filter_with_category(self):
        cat1 = Category.objects.get(slug="cat1")
        cat2 = Category.objects.get(slug="cat2")
        data = ItemViewsTestMixin.valid_item_data.copy()
        data["slug"] = "my-new-item"
        item2 = Item.objects.create(submitted_by_id=1,
                                    provider_id=1,
                                    category=cat2,
                                    **data)
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(
            reverse("items:current_user_items") + f"?cat={cat1.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)
        self.assertTemplateUsed(response, "items/item/list.html")
        items = response.context["items"]
        self.assertEqual(len(items), 2)
        self.assertNotEqual(items[0].slug, item2.slug)

    def test_current_user_item_list_only_works_if_loggedin(self):
        response = self.client.get(reverse("items:current_user_items"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"), "Not redirecting to login page")