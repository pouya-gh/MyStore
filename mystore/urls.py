"""
URL configuration for mystore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from items.views import ItemListView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
import django_eventstream

from payment.views import webhook as stripe_webhook

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("items/", include("items.urls", namespace="items")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("payment/", include("payment.urls", namespace="payment")),
    path('rosetta/', include('rosetta.urls')),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("", view=ItemListView.as_view(), name="home"),
    path("", include("account.urls", namespace="account")),
)

urlpatterns += [
    path("payment/webhook", view=stripe_webhook, name="stripe-webhook"),
    path("events/", include(django_eventstream.urls), {"channels": ["test"]}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
