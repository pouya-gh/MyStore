from django.test import TestCase
from django.contrib.auth import get_user_model

from account.models import ProviderProfile
from items.models import Item
from ..models import Order, OrderItem

from decimal import Decimal


class SetupTestDataMixin:
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

        item1 = Item.objects.create(submitted_by=user,
                                    provider=provider,
                                    name="Shoes",
                                    slug="shoes",
                                    properties='{"size= "8", "color= "white" }',
                                    description="a pair of very good shoes",
                                    remaining_items=100,
                                    price=10.00)

        item2 = Item.objects.create(submitted_by=user,
                                    provider=provider,
                                    name="Coffee",
                                    slug="coffee",
                                    properties='{"size= "big"}',
                                    description="This is some serious gourmet shit",
                                    remaining_items=100,
                                    price=99.99)

        order = Order.objects.create(customer=user)
        order.order_items.create(item=item1,
                                 sku="shoes-white-8",
                                 properties=item1.properties,
                                 quantity=2)
        order.order_items.create(item=item2,
                                 sku="coffee-big",
                                 properties=item2.properties,
                                 quantity=1)


class OrderModelTests(SetupTestDataMixin,
                      TestCase):
    def test_order_to_string_converter(self):
        order = Order.objects.first()

        self.assertEqual(str(order), str(order.id))

    def test_get_total_price(self):
        order = Order.objects.first()

        self.assertEqual(order.get_total_price(), Decimal("119.99"))

    def test_get_absolute_url(self):
        order = Order.objects.first()

        self.assertEqual(order.get_absolute_url(), f"/en/orders/{order.id}")


class OrderItemModelTests(SetupTestDataMixin,
                          TestCase):
    def test_order_to_string_converter(self):
        order_item = OrderItem.objects.first()

        self.assertEqual(str(order_item), "Order for 2 of Shoes")
