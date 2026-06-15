from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("add/", views.cart_add_ajax, name="cart_add_ajax"),
    path("data/", views.cart_data, name="cart_data"),
    path("update/", views.cart_update, name="cart_update"),

    path("calculate-shipping/", views.calculate_shipping, name="calculate_shipping"),
    path("select-shipping/", views.select_shipping, name="select_shipping"),

    path("checkout/mercadopago/", views.checkout_mercadopago_cart, name="checkout_mercadopago_cart"),
    path("mercadopago/webhook/", views.mercadopago_webhook, name="mercadopago_webhook"),
    
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),

    path("checkout/", views.checkout_page, name="checkout_page"),
]