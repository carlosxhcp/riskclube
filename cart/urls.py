from django.urls import path
from . import views

urlpatterns = [
    path("infinitepay/checkout/", views.checkout_infinitepay, name="checkout_infinitepay"),
    path("infinitepay/retorno/", views.infinitepay_return, name="infinitepay_return"),
    path("infinitepay/webhook/", views.infinitepay_webhook, name="infinitepay_webhook"),
]