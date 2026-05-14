from django.urls import path
from . import views

urlpatterns = [
    path("stripe/checkout/", views.checkout_stripe, name="checkout_stripe"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("stripe/sucesso/", views.stripe_success, name="stripe_success"),
]