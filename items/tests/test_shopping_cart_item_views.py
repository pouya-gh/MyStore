from django import test
from django.urls import reverse
from django.contrib.auth import get_user_model

from account.models import ProviderProfile
from ..models import ShoppingCartItem, Item, Category


class ShoppingCartSetupTestDataMixin:
    valid_item_data = {"name": "Shoes",
                       "slug": "shoes",
                       "properties": '{"size": "8", "color": "white" }',
                       "description": "a pair of very good shoes",
                       "submission_status": "VF",
                       "remaining_items": 100}

    @classmethod
    def setUpTestData(cls):
        user1 = get_user_model().objects.create_user(
            username="user1", password="user1user1")
        user1.save()

        provider1 = ProviderProfile.objects.create(user=user1,
                                                   official_name="official name",
                                                   social_code="1234567890",
                                                   country="IR",
                                                   province="province",
                                                   city="city",
                                                   address="123 fake street",
                                                   phone_number="09345786523",
                                                   phone_number2="09345786222",)

        category = Category.objects.create(name="Cat 1",
                                           slug="cat1")

        Item.objects.create(submitted_by=user1,
                            provider=provider1,
                            category=category,
                            **ShoppingCartSetupTestDataMixin.valid_item_data)


class TestAddShoppingCartItemView(ShoppingCartSetupTestDataMixin,
                                  test.TestCase):

    def test_add_to_shopping_cart_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.post(
            "/en/items/add_to_cart/1", data={"quantity": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{\"message\": \"added!\"}")

    def test_add_to_shopping_cart_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        url = reverse("items:add_to_cart", kwargs={"pk": 1})
        response = self.client.post(url, data={"quantity": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{\"message\": \"added!\"}")

    def test_add_to_cart_only_works_when_signed_in(self):
        response = self.client.post(
            "/en/items/add_to_cart/1", data={"quantity": 2})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/en/login"))

    def test_add_to_cart_works(self):
        # just making sure it was empty before the request
        self.assertEqual(ShoppingCartItem.objects.filter(
            customer_id=1).count(), 0)

        self.client.login(username="user1", password="user1user1")
        url = reverse("items:add_to_cart", kwargs={"pk": 1})
        response = self.client.post(url, data={"quantity": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{\"message\": \"added!\"}")
        self.assertEqual(ShoppingCartItem.objects.filter(
            customer_id=1).count(), 1)

    def test_only_adds_an_item_to_cart_once(self):
        item = Item.objects.first()
        ShoppingCartItem.objects.create(customer_id=1,
                                        item_id=1,
                                        properties=item.properties,
                                        quantity=2)
        self.client.login(username="user1", password="user1user1")
        url = reverse("items:add_to_cart", kwargs={"pk": 1})
        response = self.client.post(url, data={"quantity": 2})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ShoppingCartItem.objects.count(), 1)


class ShoppingCartItemDeleteViewTests(ShoppingCartSetupTestDataMixin,
                                      test.TestCase):
    def setUp(self):
        item = Item.objects.first()
        ShoppingCartItem.objects.create(customer_id=1,
                                        item_id=1,
                                        properties=item.properties,
                                        quantity=2)

    def test_delete_cart_item_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.post("/en/items/delete_from_cart/1")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/en/items/my_cart")
        self.assertEqual(ShoppingCartItem.objects.count(), 0)

    def test_delete_cart_item_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.post(
            reverse("items:delete_from_cart", args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/en/items/my_cart")
        self.assertEqual(ShoppingCartItem.objects.count(), 0)

    def test_delete_view_works_only_signed_in(self):
        response = self.client.post(
            reverse("items:delete_from_cart", args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/en/login"))
        self.assertEqual(ShoppingCartItem.objects.count(), 1)


class ShoppingCartItemUpdateViewTests(ShoppingCartSetupTestDataMixin,
                                      test.TestCase):
    def setUp(self):
        item = Item.objects.first()
        ShoppingCartItem.objects.create(customer_id=1,
                                        item_id=1,
                                        properties=item.properties,
                                        quantity=2)

    def test_update_cart_item_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.post(
            "/en/items/update_cart_item/1",
            data={"quantity": 3})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{\"message\": \"updated!\"}")
        new_quant = ShoppingCartItem.objects.filter(
            customer_id=1, item_id=1).first().quantity
        self.assertEqual(new_quant, 3)

    def test_update_cart_item_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.post(
            reverse("items:update_cart_item", args=[1]),
            data={"quantity": 3})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"{\"message\": \"updated!\"}")
        new_quant = ShoppingCartItem.objects.filter(
            customer_id=1, item_id=1).first().quantity
        self.assertEqual(new_quant, 3)

    def test_update_view_works_only_signed_in(self):
        response = self.client.post(
            reverse("items:update_cart_item", args=[1]),
            data={"quantity": 3})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/en/login"))
        new_quant = ShoppingCartItem.objects.filter(
            customer_id=1, item_id=1).first().quantity
        self.assertEqual(new_quant, 2)


class ShoppingCartListViewTests(ShoppingCartSetupTestDataMixin,
                                test.TestCase):
    def setUp(self):
        item = Item.objects.first()
        ShoppingCartItem.objects.create(customer_id=1,
                                        item_id=1,
                                        properties=item.properties,
                                        quantity=2)

    def test_cart_list_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/en/items/my_cart")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "items/shopping_cart/current_user_cart.html")
        self.assertIn("cart_items", response.context)

    def test_cart_list_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("items:current_user_cart"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "items/shopping_cart/current_user_cart.html")
        self.assertIn("cart_items", response.context)

    def test_cart_list_view_works_only_signed_in(self):
        response = self.client.get(reverse("items:current_user_cart"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/en/login"))
