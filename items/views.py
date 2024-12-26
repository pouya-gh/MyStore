from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Item


class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    context_object_name = "items"


class ItemDetailView(DetailView):
    model = Item
    template_name = "items/detail.html"
    context_object_name = "item"
