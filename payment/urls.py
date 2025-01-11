from django.urls import path
from . import views

app_name = "payment"
urlpatterns = [
    path("start/<uuid:order_id>", view=views.start_payment, name="start"),
    path("success", view=views.payment_success, name="success"),
    path("cancel", view=views.payment_cancel, name="cancel"),
    path("webhook", view=views.webhook, name="webhook"),
]
