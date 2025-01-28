from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http.response import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import Item, Category, ShoppingCartItem
from .forms import ItemForm, ShoppingCartForm


class ItemListView(ListView):
    model = Item
    template_name = "items/item/list.html"
    context_object_name = "items"

    def get_queryset(self):
        category_slug = self.request.GET.get("cat", None)
        if self.request.GET and category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            return Item.objects.verified_items().filter(category=category)

        return Item.objects.verified_items()


class CurrentUserItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = "items/item/list.html"
    context_object_name = "items"

    def get_queryset(self):
        user = self.request.user
        category_slug = self.request.GET.get("cat", None)
        if self.request.GET and category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            return user.submitted_items.filter(category=category)

        return user.submitted_items.all()


# you will be able to view unverified items but you won't be able to add them to shopping cart.
# this is so the item owner is able to view and edit their own items
class ItemDetailView(DetailView):
    model = Item
    template_name = "items/item/detail.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if ShoppingCartItem.objects.filter(customer=self.request.user,
                                               item=self.get_object()).exists():
                context["already_in_cart"] = True
            else:
                context["shopping_cart_form"] = ShoppingCartForm()
        return context


class LoadOnlyOwnedItemsMixin:
    def get_queryset(self):
        return self.request.user.submitted_items


# not using verfield_items queryset for item update and delete views because these are used by the item owner anyway
class ItemUpdateView(LoginRequiredMixin,
                     LoadOnlyOwnedItemsMixin,
                     UpdateView):
    model = Item
    template_name = 'items/item/form.html'
    form_class = ItemForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.submission_status = Item.ItemSubmissionStatus.PENDING
        self.object.save()
        return super().form_valid(form)


class ItemDeleteView(LoginRequiredMixin,
                     LoadOnlyOwnedItemsMixin,
                     DeleteView):
    model = Item
    success_url = reverse_lazy("items:items_list")
    template_name = 'items/item/confirm_delete.html'


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = "items/item/form.html"
    form_class = ItemForm

    def form_valid(self, form):
        # i have to do this here too for item creation. but for item update
        # it gets checked in the model.
        self.object = form.save(commit=False)
        if self.object.provider.user_id == self.request.user.id:
            self.object.submitted_by = self.request.user
            self.object.save()
            return super().form_valid(form)
        else:
            form.add_error("provider",
                           ValidationError("item provider is not owned by you"))
            return self.form_invalid(form)


@login_required
@require_POST
def add_to_shopping_cart(request, pk):
    # you can only add verfied items
    item = get_object_or_404(Item.objects.verified_items(), id=pk)
    user = request.user
    if not ShoppingCartItem.objects.filter(item=item, customer=user).exists():
        form = ShoppingCartForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user.shopping_cart_items.create(item=item,
                                            properties=item.properties,
                                            quantity=cd["quantity"])
            return JsonResponse({"message": "added!"})

    return HttpResponseBadRequest("Can't add to cart!")


@login_required
@require_POST
def delete_from_shopping_cart(request, pk):
    cart_item = get_object_or_404(
        ShoppingCartItem, item_id=pk, customer=request.user)
    cart_item.delete()

    return redirect(reverse("items:current_user_cart"))


@login_required
@require_POST
def update_cart_item_quantity(request, pk):
    form = ShoppingCartForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart_item = get_object_or_404(
            ShoppingCartItem, item_id=pk, customer=request.user)
        cart_item.quantity = cd["quantity"]
        cart_item.save()
        return JsonResponse({"message": "updated!"})

    return HttpResponseBadRequest("Can't update cart!")


@login_required
def current_user_shopping_cart_details(request):
    cart_items = ShoppingCartItem.objects.filter(customer=request.user)

    return render(request,
                  "items/shopping_cart/current_user_cart.html",
                  context={"cart_items": cart_items})


@login_required
def get_current_user_shopping_cart_item_count(request):
    count = ShoppingCartItem.objects.filter(customer=request.user).count()

    return JsonResponse({"count": count})
