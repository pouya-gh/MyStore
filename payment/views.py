from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.conf import settings
import stripe.error
import stripe.webhook

from orders.models import Order

import stripe

from decimal import Decimal

stripe.api_key = settings.STRIPE_API_KEY


@login_required
def start_payment(request, order_id):
    order = get_object_or_404(request.user.orders.filter(
        status=Order.OrderStatus.PENDING), id=order_id)
    session_params = {
        "client_reference_id": order.id,
        "line_items": [],
        "mode": 'payment',
        "success_url": request.build_absolute_uri(reverse("payment:success")) + "?session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": request.build_absolute_uri(reverse("payment:cancel")),
    }
    for order_item in order.order_items.all():
        session_params["line_items"].append({
            "price_data": {
                "unit_amount": int(order_item.item.price * Decimal(100)),
                "currency": order_item.item.currency.lower(),
                "product_data": {"name": order_item.sku},
            },
            'quantity': order_item.quantity
        })
    session = stripe.checkout.Session.create(**session_params)

    return redirect(session.url, code=303)


@login_required
def payment_success(request):
    # session_id = request.GET["session_id"]
    # session = stripe.checkout.Session.retrieve(session_id)
    # return render(request, "payment/success.html", {"session": session})
    return render(request, "payment/success.html")


@login_required
def payment_cancel(request):
    return render(request, "payment/cancel.html")


@csrf_exempt
@require_POST
def webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_ENDPOINT_SECRET
    sig_header = request.headers['STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            request.body, sig_header, endpoint_secret)
    except ValueError as e:
        raise e
    except stripe.error.SignatureVerificationError as e:
        raise e

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # order = get_object_or_404(Order, id=session["client_reference_id"])
        try:
            Order.objects.filter(id=session["client_reference_id"]).\
                update(status=Order.OrderStatus.PAYMENT_ACCEPTED,
                       payment_id=session["payment_intent"])
        except Order.DoesNotExist:
            raise Http404("Order does not exits")
        # order.status = Order.OrderStatus.PAYMENT_ACCEPTED
        # order.payment_id = session["payment_intent"]
        # order.save()
    else:
        print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(str(event), status=200)
