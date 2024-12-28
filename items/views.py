from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item
from .forms import ItemForm


class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    context_object_name = "items"


class ItemDetailView(DetailView):
    model = Item
    template_name = "items/detail.html"
    context_object_name = "item"

class LoadOnlyOwnedItemsMixin:
    def get_queryset(self):
        return self.request.user.submitted_items

class ItemUpdateView(LoginRequiredMixin,
                     LoadOnlyOwnedItemsMixin,
                     UpdateView):
    model = Item
    template_name = 'items/form.html'
    form_class = ItemForm
    
class ItemDeleteView(LoginRequiredMixin,
                     LoadOnlyOwnedItemsMixin,
                     DeleteView):
    model = Item
    success_url = reverse_lazy("items:items_list")
    

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = "items/form.html"
    form_class = ItemForm
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.submitted_by = self.request.user
        self.object.save()
        return super().form_valid(form)
    