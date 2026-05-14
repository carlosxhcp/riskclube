from django.urls import path
from . import views

urlpatterns = [
    path("infinitepay/checkout/", views.checkout_infinitepay, name="checkout_infinitepay"),
]