from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http.response import Http404

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

from items.models import ShoppingCartItem
from .models import Order, OrderItem


@login_required
def order_create(request):
    user = request.user
    if user.shopping_cart_items.count() == 0:
        return redirect(reverse("home"))
    order = Order.objects.create(customer=user)
    for cart_item in user.shopping_cart_items.all():
        order.order_items.create(item=cart_item.item,
                                 sku=cart_item.generate_sku(),
                                 quantity=cart_item.quantity,
                                 properties=cart_item.properties)

    user.shopping_cart_items.all().delete()

    return redirect(reverse("orders:order_details", args=[order.id]))


@login_required
def order_details(request, order_id):
    order = get_object_or_404(request.user.orders, id=order_id)

    return render(request, "orders/details.html", {"order": order})

@login_required
@require_POST
def order_cancel(request, id):
    try:
        result = request.user.orders.filter(id=id).update(status=Order.OrderStatus.CANCELED)
    except Order.DoesNotExist:
        raise Http404("Order does not exist or it doesn't belong to you.")
    
    if result == 0:
        raise Http404("Order does not exist or it doesn't belong to you.")
    
    return redirect(reverse("orders:order_details", args=[id]))


@login_required
def user_orders(request):
    orders = request.user.orders.all()

    return render(request, "orders/list.html", {"orders": orders})
