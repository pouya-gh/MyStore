from django.forms import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name",
                  "slug",
                  "provider",
                  "properties",
                  "description",
                  "remaining_items",]
