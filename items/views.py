from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Item


class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    context_object_name = "items"
