from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name",
                  "slug",
                  "provider",
                  "properties",
                  "description",
                  "price",
                  "remaining_items",
                  "category"]


class ShoppingCartForm(forms.Form):
    template_name = "items/shopping_cart/form.html"
    quantity = forms.IntegerField(min_value=1)
