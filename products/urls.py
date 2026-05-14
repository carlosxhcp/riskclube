from django.urls import path
from . import views

urlpatterns = [
    path(
        "produto/<slug:slug>/checkout/",
        views.checkout_stripe_product,
        name="checkout_stripe_product"
    ),
]