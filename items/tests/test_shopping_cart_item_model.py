from django import test
from django.contrib.auth import get_user_model

from account.models import ProviderProfile
from ..models import ShoppingCartItem, Item, Category


class ShoppingCartItemTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()

        user1 = user_model.objects.create_user(
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
        valid_item_data = {"name": "Shoes",
                           "slug": "shoes",
                           "properties": {"size": ["8"], "color": ["white"], },
                           "description": "a pair of very good shoes",
                           "remaining_items": 100}
        item = Item.objects.create(submitted_by=user1,
                                   provider=provider1,
                                   category=category,
                                   **valid_item_data)

        ShoppingCartItem.objects.create(customer=user1,
                                        item=item,
                                        quantity=1,
                                        properties={"size": "8", "color": "white"})

    def test_shopping_cart_item_name(self):
        cart_item = ShoppingCartItem.objects.first()
        self.assertEqual(
            str(cart_item), f"{cart_item.quantity} {cart_item.item.name}")

    def test_shopping_cart_item_sku(self):
        cart_item = ShoppingCartItem.objects.first()
        sku = cart_item.item.slug
        sorted_props = sorted(cart_item.properties.items())
        for _, v in sorted_props:
            sku += "-" + v.lower()
        self.assertEqual(cart_item.generate_sku(), sku)
