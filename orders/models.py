from django.db import models
from django.conf import settings
from django.urls import reverse

from items.models import Item

import uuid


class OrderItem(models.Model):
    order = models.ForeignKey("Order",
                              on_delete=models.CASCADE,
                              related_name="order_items")
    item = models.ForeignKey(Item,
                             on_delete=models.PROTECT)
    sku = models.SlugField(max_length=255,
                           blank=False,
                           null=False,
                           default=None)
    quantity = models.PositiveIntegerField(null=False, blank=False)
    properties = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.quantity} of {self.item}"


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PN", "Pending"
        PAYMENT_ACCEPTED = "PA", "Payment Accepted"
        PAYMENT_DECLINED = "PD", "Payment Declined"
        CANCELED = "CN", "Canceled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.PROTECT,
                                 related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=OrderStatus,
                              default=OrderStatus.PENDING)
    payment_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.id)

    def get_total_price(self):
        price = 0
        for oi in self.order_items.all():
            price += oi.item.price * oi.quantity

        return price

    def get_absolute_url(self):
        return reverse("orders:order_details", kwargs={"order_id": self.id})
