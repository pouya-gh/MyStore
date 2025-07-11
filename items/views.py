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
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _

from django_eventstream import send_event

from .models import Item, Category, ShoppingCartItem, is_alphnum_and_space
from .forms import ItemForm, ShoppingCartForm
from tracker.models import SiteVisitTracker
from tracker.tasks import get_ip_location

import json
import urllib.request
from decimal import Decimal, InvalidOperation


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
    
    def get(self, request, *args, **kwargs):
        """
        hadles site's visit tracker for every request coming through this view.
        i should be using asyn tasks for this but i'm using render's free hosts to 
        host this work sample, so i have no choice.
        """
        curr_ip = request.META["REMOTE_ADDR"]
        try:
            tracker = SiteVisitTracker.objects.get(ip=curr_ip)
            tracker.counter += 1
            tracker.save()
        except SiteVisitTracker.DoesNotExist:
            if SiteVisitTracker.objects.count() >= 500:
                SiteVisitTracker.objects.last().delete()
            # trying to figure out ip location.
            with urllib.request.urlopen(f"http://ip-api.com/json/{curr_ip}") as url:
                data = url.read().decode()
                j = json.loads(data)
            try:
                location = f"{j['country']}:{j['regionName']}:{j['city']}"
            except KeyError:
                location = "something went wrong"
            tracker = SiteVisitTracker.objects.create(ip=curr_ip, location=location)
            # i can't use celery for now because i'm going to use render's free version
            # get_ip_location.delay(curr_ip)

        return super().get(request, *args, **kwargs)


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


class ItemUpdateAndCreateToolsMixin:
    def strip_and_capitalize_props_keys(self, props: dict):
        """
        Strip begining and trailing spaces from property keys and capitalize
        the first letters to make searching with them as filters easier. 
        """
        props_to_change = []
        for k, v in props.items():
            new_k = k.strip().capitalize()
            if k != new_k:
                props_to_change.append([k, v, new_k])
        for p in props_to_change:
            del props[p[0]]
            props[p[2]] = p[1]


# not using verfield_items queryset for item update and delete views because these are used by the item owner anyway
class ItemUpdateView(LoginRequiredMixin,
                     LoadOnlyOwnedItemsMixin,
                     ItemUpdateAndCreateToolsMixin,
                     UpdateView):
    model = Item
    template_name = 'items/item/form.html'
    form_class = ItemForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.submission_status = Item.ItemSubmissionStatus.PENDING
        if self.object.properties:
            self.strip_and_capitalize_props_keys(self.object.properties)

        self.object.save()
        return super().form_valid(form)


class ItemDeleteView(LoginRequiredMixin,
                     LoadOnlyOwnedItemsMixin,
                     DeleteView):
    model = Item
    success_url = reverse_lazy("items:items_list")
    template_name = 'items/item/confirm_delete.html'


class ItemCreateView(LoginRequiredMixin,
                     ItemUpdateAndCreateToolsMixin,
                     CreateView):
    model = Item
    template_name = "items/item/form.html"
    form_class = ItemForm

    def form_valid(self, form):
        # i have to do this here too for item creation. but for item update
        # it gets checked in the model.
        self.object = form.save(commit=False)
        if self.object.properties:
            self.strip_and_capitalize_props_keys(self.object.properties)
        if self.object.provider.user_id == self.request.user.id:
            self.object.submitted_by = self.request.user
            self.object.save()
            return super().form_valid(form)
        else:
            form.add_error("provider",
                           ValidationError(_("Item provider is not owned by you.")))
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
            send_event(f"user:{user.id}", "cart_message", user.shopping_cart_items.count())
            return JsonResponse({"message": "added!"})
    # else:
    #     messages.warning(request, "Item is already in cart!")

    return HttpResponseBadRequest(_("Can't add to cart!"))


@login_required
@require_POST
def delete_from_shopping_cart(request, pk):
    cart_item = get_object_or_404(
        ShoppingCartItem, item_id=pk, customer=request.user)
    cart_item.delete()
    send_event(f"user:{request.user.id}", "cart_message", request.user.shopping_cart_items.count())
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

    return HttpResponseBadRequest(_("Can't update cart!"))


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


def search_items(request):
    q = request.GET.get('q')
    filters = request.GET.get('filters')
    category_id = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    items = Item.objects.verified_items().only("name", "category", "price")

    categories = Category.objects.only("name")

    if min_price:
        try:
            items = items.filter(price__gte=Decimal(min_price))
        except InvalidOperation:
            messages.warning(request, _("Invalid min price input."))

    if max_price:
        try:
            items = items.filter(price__lte=Decimal(max_price))
        except InvalidOperation:
            messages.warning(request, _("Invalid max price input."))

    if q:
        items = items.filter(name__icontains=q)

    if filters:
        q_filters = Q()
        filters_list = json.loads(filters)
        for f in filters_list:
            # this is to make searching easier
            f_name_stripped_capped = f[0].strip().capitalize()
            # making sure they are safe from SQL injection
            if not is_alphnum_and_space(f_name_stripped_capped):
                msg = _("Filter name {filter_name} was ignored. Only alphanumeric characters and space are allowed.").format(
                    filter_name=f[0])
                messages.warning(request, msg)
                continue
            q_filters.add(
                Q(**{f"properties__{f_name_stripped_capped}__icontains": f[1]}), Q.AND)
        items = items.filter(q_filters)

    if category_id:
        category_and_children = [int(category_id)]
        cat_children_ids = Category.objects.only("id").filter(parent_id=category_id)
        for child in cat_children_ids:
            category_and_children.append(int(child.id))
        items = items.filter(category_id__in=category_and_children)

    if not (q or filters or category_id or min_price or max_price):
        items = []

    return render(request, "items/item/search.html", {"items": items, "categories": categories})
