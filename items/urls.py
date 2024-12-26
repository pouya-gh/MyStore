from django.urls import path
from . import views

app_name = "items"
urlpatterns = [
    path("", view=views.ItemListView.as_view(), name="items_list"),
    path("<pk>/", view=views.ItemDetailView.as_view(), name="item_details"),
]
