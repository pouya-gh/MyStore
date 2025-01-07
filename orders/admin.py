from django.contrib import admin
from .models import Order, OrderItem

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "item", "quantity", "created_at"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status"]