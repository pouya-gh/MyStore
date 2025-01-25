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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            # visible.label_tag(attrs={"class": "label-control"})


class ShoppingCartForm(forms.Form):
    template_name = "items/shopping_cart/form.html"
    quantity = forms.IntegerField(min_value=1)
