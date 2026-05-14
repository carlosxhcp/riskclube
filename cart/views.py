import json
import requests

from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from products.models import Product


def checkout_infinitepay(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,

        "redirect_url": f"{settings.SITE_URL}/sucesso/",

        "items": [
            {
                "quantity": 1,

                "price": int(product.price * 100),

                "description": product.name
            }
        ]
    }

    response = requests.post(
        "https://api.checkout.infinitepay.io/links",
        json=payload,
        timeout=15
    )

    print(response.status_code)
    print(response.text)

    if response.status_code not in [200, 201]:
        return HttpResponseBadRequest(response.text)

    data = response.json()

    return redirect(data["url"])


def cart_data(request):

    cart = request.session.get("cart", {})

    items = []
    subtotal = Decimal("0.00")

    for cart_key, item in cart.items():

        quantity = int(item.get("quantity", 1))
        price = Decimal(str(item.get("price", 0)))

        item_subtotal = price * quantity

        subtotal += item_subtotal

        items.append({
            "cart_key": cart_key,
            "name": item.get("name", "Produto"),
            "size": item.get("size", ""),
            "quantity": quantity,
            "price": float(price),
            "subtotal": float(item_subtotal),
            "image": item.get("image", ""),
            "installments": f"6x de R$ {(price / 6):.2f}".replace(".", ","),
        })

    free_shipping_limit = Decimal("200.00")

    remaining = free_shipping_limit - subtotal

    if remaining < 0:
        remaining = Decimal("0.00")

    progress = min(
        (subtotal / free_shipping_limit) * 100,
        100
    ) if free_shipping_limit > 0 else 0

    return JsonResponse({
        "items": items,
        "subtotal": float(subtotal),
        "discount": 0,
        "total": float(subtotal),
        "free_shipping_remaining": float(remaining),
        "free_shipping_progress": float(progress),
    })


@require_POST
def cart_add_ajax(request):

    data = json.loads(request.body)

    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    cart_key = str(product.id)

    if cart_key in cart:

        cart[cart_key]["quantity"] += quantity

    else:

        cart[cart_key] = {
            "product_id": product.id,
            "name": product.name,
            "price": str(product.price),
            "quantity": quantity,
            "size": "900ML",
            "image": product.image.url if product.image else "",
        }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "success": True
    })


@require_POST
def cart_update(request):

    data = json.loads(request.body)

    cart_key = str(data.get("cart_key"))
    action = data.get("action")

    cart = request.session.get("cart", {})

    if cart_key not in cart:
        return JsonResponse({
            "success": False
        })

    if action == "increase":

        cart[cart_key]["quantity"] += 1

    elif action == "decrease":

        cart[cart_key]["quantity"] -= 1

        if cart[cart_key]["quantity"] <= 0:
            del cart[cart_key]

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "success": True
    })


def checkout_infinitepay_cart(request):

    cart = request.session.get("cart", {})

    if not cart:
        return HttpResponseBadRequest("Carrinho vazio.")

    items = []

    for cart_key, item in cart.items():

        items.append({
            "quantity": int(item.get("quantity", 1)),
            "price": int(
                Decimal(str(item.get("price", 0))) * 100
            ),
            "description": item.get("name", "Produto")
        })

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,

        "redirect_url": f"{settings.SITE_URL}/sucesso/",

        "items": items
    }

    response = requests.post(
        "https://api.checkout.infinitepay.io/links",
        json=payload,
        timeout=15
    )

    print(response.status_code)
    print(response.text)

    if response.status_code not in [200, 201]:
        return HttpResponseBadRequest(response.text)

    data = response.json()

    return redirect(data["url"])