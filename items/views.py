from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from .models import Item, Category
from .forms import ItemForm


class ItemListView(ListView):
    model = Item
    template_name = "items/list.html"
    context_object_name = "items"

    def get_queryset(self):
        category_slug = self.request.GET.get("cat", None)
        if self.request.GET and category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            return Item.objects.filter(category=category)

        return Item.objects.all()


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
        if self.object.provider.user_id == self.request.user.id:
            self.object.submitted_by = self.request.user
            self.object.save()
            return super().form_valid(form)
        else:
            form.add_error("provider",
                           ValidationError("item provider is not owned by you"))
            return self.form_invalid(form)
