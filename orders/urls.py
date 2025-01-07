from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("new", view=views.order_create, name="place_order"),
    path("my_orders", view=views.user_orders, name="user_orders_list"),
    path("<uuid:order_id>", view=views.order_details, name="order_details"),
]
