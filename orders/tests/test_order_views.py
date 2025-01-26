from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from account.models import ProviderProfile
from items.models import Item, ShoppingCartItem
from ..models import Order, OrderItem

from decimal import Decimal


class SetupOrderViewsTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user = user_model.objects.create_user(
            username="user1", password="user1user1")
        user.save()

        user2 = user_model.objects.create_user(
            username="user2", password="user2user2")
        user2.save()

        provider = ProviderProfile.objects.create(user=user,
                                                  official_name="official name",
                                                  social_code="1234567890",
                                                  country="IR",
                                                  province="province",
                                                  city="city",
                                                  address="123 fake street",
                                                  phone_number="09345786523",
                                                  phone_number2="09345786222",)

        item1 = Item.objects.create(submitted_by=user,
                                    provider=provider,
                                    name="Shoes",
                                    slug="shoes",
                                    properties={"size": "8", "color": "white"},
                                    description="a pair of very good shoes",
                                    remaining_items=100,
                                    price=10.00)

        item2 = Item.objects.create(submitted_by=user,
                                    provider=provider,
                                    name="Coffee",
                                    slug="coffee",
                                    properties={"size": "big"},
                                    description="This is some serious gourmet shit",
                                    remaining_items=100,
                                    price=99.99)

        ShoppingCartItem.objects.create(customer=user,
                                        item=item1,
                                        properties=item1.properties,
                                        quantity=2)

        ShoppingCartItem.objects.create(customer=user,
                                        item=item2,
                                        properties=item2.properties,
                                        quantity=1)


class OrdersCreateViewTests(SetupOrderViewsTestDataMixin,
                            TestCase):
    def test_create_order_url_exists(self):
        self.client.login(username="user1", password="user1user1")

        self.assertEqual(Order.objects.count(), 0)
        response = self.client.get("/orders/new")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(response.url, order.get_absolute_url())

    def test_create_order_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")

        self.assertEqual(Order.objects.count(), 0)
        response = self.client.get(reverse("orders:place_order"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(response.url, order.get_absolute_url())

    def test_create_order_only_works_if_logged_in(self):
        response = self.client.get(reverse("orders:place_order"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ShoppingCartItem.objects.count(), 2)
        self.assertTrue(response.url.startswith("/login"))

    def test_shopping_cart_is_emptied_after_order_creation(self):
        self.client.login(username="user1", password="user1user1")

        self.assertEqual(ShoppingCartItem.objects.count(), 2)
        response = self.client.get(reverse("orders:place_order"))
        self.assertEqual(ShoppingCartItem.objects.count(), 0)

    def test_create_order_redirects_home_if_cart_is_empty(self):
        self.client.login(username="user1", password="user1user1")

        ShoppingCartItem.objects.all().delete()
        response = self.client.get(reverse("orders:place_order"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.url, "/")


class OrderDetailViewTests(SetupOrderViewsTestDataMixin,
                           TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user = get_user_model().objects.get(username="user1")
        item1 = Item.objects.get(pk=1)
        item2 = Item.objects.get(pk=2)
        order = Order.objects.create(customer=user)
        order.order_items.create(item=item1,
                                 sku="shoes-white-8",
                                 properties=item1.properties,
                                 quantity=2)
        order.order_items.create(item=item2,
                                 sku="coffee-big",
                                 properties=item2.properties,
                                 quantity=1)

    def test_order_detail_url_exists(self):
        order = Order.objects.first()
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(f"/orders/{order.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("order", response.context)
        self.assertTemplateUsed(response, "orders/details.html")

    def test_order_detail_url_has_correct_name(self):
        order = Order.objects.first()
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(
            reverse("orders:order_details", args=[order.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("order", response.context)
        self.assertTemplateUsed(response, "orders/details.html")

    def test_order_detail_only_works_if_loggedin(self):
        order = Order.objects.first()
        response = self.client.get(order.get_absolute_url())

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_order_detail_only_loads_current_user_orders(self):
        order = Order.objects.first()
        self.client.login(username="user2", password="user2user2")
        response = self.client.get(
            reverse("orders:order_details", args=[order.id]))

        self.assertEqual(response.status_code, 404)


class OrdersListViewTests(SetupOrderViewsTestDataMixin,
                          TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user = get_user_model().objects.get(username="user1")
        item1 = Item.objects.get(pk=1)
        item2 = Item.objects.get(pk=2)
        order = Order.objects.create(customer=user)
        order.order_items.create(item=item1,
                                 sku="shoes-white-8",
                                 properties=item1.properties,
                                 quantity=2)
        order.order_items.create(item=item2,
                                 sku="coffee-big",
                                 properties=item2.properties,
                                 quantity=1)

    def test_orders_list_view_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get("/orders/my_orders")

        self.assertEqual(response.status_code, 200)
        self.assertIn("orders", response.context)
        orders = response.context['orders']
        self.assertEqual(len(orders), 1)
        self.assertTemplateUsed(response, "orders/list.html")

    def test_orders_list_view_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        response = self.client.get(reverse("orders:user_orders_list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("orders", response.context)
        orders = response.context['orders']
        self.assertEqual(len(orders), 1)
        self.assertTemplateUsed(response, "orders/list.html")

    def test_orders_list_only_works_if_loggedin(self):
        response = self.client.get(reverse("orders:user_orders_list"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_order_detail_only_loads_current_user_orders(self):
        self.client.login(username="user2", password="user2user2")
        response = self.client.get(reverse("orders:user_orders_list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("orders", response.context)
        orders = response.context['orders']
        self.assertEqual(len(orders), 0)
        self.assertTemplateUsed(response, "orders/list.html")


class OrdersCancelViewTests(SetupOrderViewsTestDataMixin,
                            TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user = get_user_model().objects.get(username="user1")
        item1 = Item.objects.get(pk=1)
        item2 = Item.objects.get(pk=2)
        order = Order.objects.create(customer=user)
        order.order_items.create(item=item1,
                                 sku="shoes-white-8",
                                 properties=item1.properties,
                                 quantity=2)
        order.order_items.create(item=item2,
                                 sku="coffee-big",
                                 properties=item2.properties,
                                 quantity=1)

    def test_order_cancel_view_url_exists(self):
        self.client.login(username="user1", password="user1user1")
        order = Order.objects.first()
        response = self.client.post("/orders/cancel/" + str(order.id))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, order.get_absolute_url())
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.CANCELED)

    def test_order_cancel_view_url_has_correct_name(self):
        self.client.login(username="user1", password="user1user1")
        order = Order.objects.first()
        response = self.client.post(reverse("orders:order_cancel", args=[order.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, order.get_absolute_url())
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.CANCELED)

    def test_order_cancel_only_works_if_loggedin(self):
        order = Order.objects.first()
        response = self.client.post(reverse("orders:order_cancel", args=[order.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/login"))

    def test_order_cancel_only_loads_current_user_orders(self):
        self.client.login(username="user2", password="user2user2")
        order = Order.objects.first()
        response = self.client.post(reverse("orders:order_cancel", args=[order.id]))

        self.assertEqual(response.status_code, 404)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.OrderStatus.PENDING)
