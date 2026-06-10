from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path(
        "produto/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),

    path(
        "produto/<slug:slug>/checkout/",
        views.checkout_stripe_product,
        name="checkout_stripe_product"
    ),
    path(
    "produto/<slug:slug>/personalizar/",
    views.customization_choice,
    name="customization_choice"
    ),
]