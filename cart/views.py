import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from products.models import Product
from django.shortcuts import get_object_or_404

#from .models import Order


def checkout_stripe(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    cart = request.session.get("cart", {})

    if not cart:
        return HttpResponseBadRequest("Carrinho vazio.")

    line_items = []

    for cart_key, item in cart.items():
        line_items.append({
            "price_data": {
                "currency": "brl",
                "product_data": {
                    "name": f"{item.get('name')} - Tam. {item.get('size', '')}",
                },
                "unit_amount": int(float(item.get("price", 0)) * 100),
            },
            "quantity": int(item.get("quantity", 1)),
        })

    shipping = request.session.get("shipping", {})
    shipping_price = float(shipping.get("price", 0))

    if shipping_price > 0:
        line_items.append({
            "price_data": {
                "currency": "brl",
                "product_data": {
                    "name": f"Frete - {shipping.get('name', 'Entrega')}",
                },
                "unit_amount": int(shipping_price * 100),
            },
            "quantity": 1,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url=f"{settings.SITE_URL}/cart/stripe/sucesso/",
        cancel_url=f"{settings.SITE_URL}/cart/",
        metadata={
            "user_id": request.user.id if request.user.is_authenticated else "",
        }
    )

    return redirect(session.url)


def checkout_stripe_product(request, slug):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    product = get_object_or_404(Product, slug=slug, available=True)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": product.name,
                    },
                    "unit_amount": int(float(product.price) * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.SITE_URL}/shop/{product.slug}/?payment=success",
        cancel_url=f"{settings.SITE_URL}/shop/{product.slug}/?payment=cancel",
        metadata={
            "product_id": product.id,
            "user_id": request.user.id if request.user.is_authenticated else "",
        }
    )

    return redirect(session.url)

from django.http import HttpResponse

def stripe_webhook(request):
    return HttpResponse(status=200)


def stripe_success(request):
    return HttpResponse("Pagamento aprovado")