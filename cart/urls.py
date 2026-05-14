from django.urls import path
from . import views

urlpatterns = [
    path(
        "infinitepay/checkout/<int:product_id>/",
        views.checkout_infinitepay,
        name="checkout_infinitepay"
    ),
]