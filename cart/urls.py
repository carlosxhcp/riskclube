from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add/", views.cart_add_ajax, name="cart_add_ajax"),
    path("data/", views.cart_data, name="cart_data"),
    path("update/", views.cart_update, name="cart_update"),

    path("calculate-shipping/", views.calculate_shipping, name="calculate_shipping"),
    path("select-shipping/", views.select_shipping, name="select_shipping"),

    path(
        "infinitepay/checkout/<int:product_id>/",
        views.checkout_infinitepay,
        name="checkout_infinitepay"
    ),

    path(
        "infinitepay/checkout/",
        views.checkout_infinitepay_cart,
        name="checkout_infinitepay_cart"
    ),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
]