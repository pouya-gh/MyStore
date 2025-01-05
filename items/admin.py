from django.contrib import admin
from .models import Item, Category, ShoppingCartItem


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "provider",
                    "submitted_by", "submission_status"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent"]
    list_filter = ["name", "parent"]


@admin.register(ShoppingCartItem)
class ShoppingCartItemAdmin(admin.ModelAdmin):
    list_display = ["item", "customer", "quantity"]
