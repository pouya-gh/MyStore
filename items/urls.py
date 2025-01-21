from django.urls import path
from . import views

app_name = "items"
urlpatterns = [
    path("", view=views.ItemListView.as_view(), name="items_list"),
    path("new", view=views.ItemCreateView.as_view(), name="item_create"),
    path("my_cart", view=views.current_user_shopping_cart_details,
         name="current_user_cart"),
    path("my_cart_count.json", view=views.get_current_user_shopping_cart_item_count,
         name="my_cart_count_json"),
    path("<pk>", view=views.ItemDetailView.as_view(), name="item_details"),
    path("update/<pk>", view=views.ItemUpdateView.as_view(), name="item_update"),
    path("delete/<pk>", view=views.ItemDeleteView.as_view(), name="item_delete"),
    path("add_to_cart/<pk>", view=views.add_to_shopping_cart, name="add_to_cart"),
    path("delete_from_cart/<pk>", view=views.delete_from_shopping_cart,
         name="delete_from_cart"),
    path("update_cart_item/<pk>", view=views.update_cart_item_quantity,
         name="update_cart_item"),
]
