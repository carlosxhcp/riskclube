import json
import requests

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from products.models import Product


FREE_SHIPPING_LIMIT = Decimal("250.00")


def to_decimal(value, default="0.00"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def money_to_cents(value):
    return int((to_decimal(value) * 100).quantize(Decimal("1")))


def clear_shipping(request):
    request.session.pop("shipping", None)
    request.session.modified = True


def get_cart_subtotal(cart):
    subtotal = Decimal("0.00")

    for item in cart.values():
        quantity = int(item.get("quantity", 1))
        price = to_decimal(item.get("price", 0))
        subtotal += price * quantity

    return subtotal


def get_cart_payload(request):
    cart = request.session.get("cart", {})
    shipping = request.session.get("shipping")

    items = []
    subtotal = Decimal("0.00")

    for cart_key, item in cart.items():
        quantity = int(item.get("quantity", 1))
        price = to_decimal(item.get("price", 0))

        item_subtotal = price * quantity
        subtotal += item_subtotal

        items.append({
            "cart_key": cart_key,
            "name": item.get("name", "Produto"),
            "size": item.get("size", ""),
            "color": item.get("color", ""),
            "engraving_name": item.get("engraving_name", ""),
            "engraving_image": item.get("engraving_image", ""),
            "quantity": quantity,
            "price": float(price),
            "subtotal": float(item_subtotal),
            "image": item.get("image", ""),
            "installments": f"6x de R$ {(price / 6):.2f}".replace(".", ","),
        })

    if subtotal >= FREE_SHIPPING_LIMIT:
        shipping = {
            "id": "free",
            "name": "Frete grátis",
            "company": "",
            "price": 0,
            "time": "",
            "cep": shipping.get("cep", "") if shipping else "",
            "icon": "",
        }

        request.session["shipping"] = shipping
        request.session.modified = True
        shipping_price = Decimal("0.00")

    else:
        if shipping and shipping.get("id") == "free":
            request.session.pop("shipping", None)
            request.session.modified = True
            shipping = None

        shipping_price = to_decimal(shipping.get("price", 0)) if shipping else Decimal("0.00")

    remaining = FREE_SHIPPING_LIMIT - subtotal

    if remaining < 0:
        remaining = Decimal("0.00")

    progress = min((subtotal / FREE_SHIPPING_LIMIT) * 100, 100)

    total = subtotal + shipping_price

    return {
        "success": True,
        "items": items,
        "subtotal": float(subtotal),
        "discount": 0,
        "shipping": shipping,
        "shipping_price": float(shipping_price),
        "total": float(total),
        "free_shipping_remaining": float(remaining),
        "free_shipping_progress": float(progress),
        "free_shipping_limit": float(FREE_SHIPPING_LIMIT),
    }


def cart_data(request):
    return JsonResponse(get_cart_payload(request))


@require_POST
def cart_add_ajax(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos.",
        }, status=400)

    product_id = data.get("product_id")

    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    size = data.get("size") or "Único"
    color = data.get("color") or ""

    engraving_name = data.get("engraving_name") or ""
    engraving_image = data.get("engraving_image") or ""

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    cart_key = f"{product.id}_{color}_{size}_{engraving_name}"

    final_image = (
        data.get("image")
        or engraving_image
        or (product.image.url if product.image else "")
    )

    if cart_key in cart:
        cart[cart_key]["quantity"] = int(cart[cart_key].get("quantity", 1)) + quantity
    else:
        cart[cart_key] = {
            "product_id": product.id,
            "name": product.name,
            "price": str(product.price),
            "quantity": quantity,
            "size": size,
            "color": color,
            "engraving_name": engraving_name,
            "engraving_image": engraving_image,
            "image": final_image,
        }

    request.session["cart"] = cart
    request.session.modified = True

    clear_shipping(request)

    payload = get_cart_payload(request)
    payload["cart_key"] = cart_key

    return JsonResponse(payload)


@require_POST
def cart_update(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos.",
        }, status=400)

    cart_key = str(data.get("cart_key"))
    action = data.get("action")
    change = data.get("change")

    cart = request.session.get("cart", {})

    if cart_key not in cart:
        return JsonResponse({
            "success": False,
            "error": "Produto não encontrado no carrinho.",
        }, status=404)

    current_quantity = int(cart[cart_key].get("quantity", 1))

    if change is not None:
        try:
            new_quantity = current_quantity + int(change)
        except (TypeError, ValueError):
            return JsonResponse({
                "success": False,
                "error": "Quantidade inválida.",
            }, status=400)

    elif action == "increase":
        new_quantity = current_quantity + 1

    elif action == "decrease":
        new_quantity = current_quantity - 1

    else:
        return JsonResponse({
            "success": False,
            "error": "Ação inválida.",
        }, status=400)

    if new_quantity <= 0:
        del cart[cart_key]
    else:
        cart[cart_key]["quantity"] = new_quantity

    request.session["cart"] = cart
    request.session.modified = True

    clear_shipping(request)

    return JsonResponse(get_cart_payload(request))


@require_POST
def calculate_shipping(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos.",
        }, status=400)

    cep = str(data.get("cep", "")).replace("-", "").replace(".", "").strip()
    cart = request.session.get("cart", {})

    if not cep or len(cep) != 8 or not cep.isdigit():
        return JsonResponse({
            "success": False,
            "error": "CEP inválido.",
        }, status=400)

    if not cart:
        return JsonResponse({
            "success": False,
            "error": "Carrinho vazio.",
        }, status=400)

    subtotal = get_cart_subtotal(cart)

    if subtotal >= FREE_SHIPPING_LIMIT:
        shipping = {
            "id": "free",
            "name": "Frete grátis",
            "company": "",
            "price": 0,
            "time": "",
            "cep": cep,
            "icon": "",
        }

        request.session["shipping"] = shipping
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "free_shipping": True,
            "options": [
                {
                    "id": "free",
                    "name": "Frete grátis",
                    "company": "",
                    "price": 0,
                    "delivery_time": "",
                    "cep": cep,
                    "icon": "",
                }
            ],
        })

    required_settings = [
        "MELHOR_ENVIO_TOKEN",
        "MELHOR_ENVIO_ORIGIN_CEP",
    ]

    for setting_name in required_settings:
        if not getattr(settings, setting_name, None):
            return JsonResponse({
                "success": False,
                "error": f"Configuração ausente: {setting_name}.",
            }, status=500)

    products = []

    for item in cart.values():
        quantity = int(item.get("quantity", 1))
        price = to_decimal(item.get("price", 0))

        products.append({
            "id": str(item.get("product_id", "")),
            "width": 20,
            "height": 5,
            "length": 30,
            "weight": 0.3,
            "insurance_value": float(price),
            "quantity": quantity,
        })

    env = getattr(settings, "MELHOR_ENVIO_ENV", "sandbox")

    base_url = (
        "https://sandbox.melhorenvio.com.br"
        if env == "sandbox"
        else "https://www.melhorenvio.com.br"
    )

    payload = {
        "from": {
            "postal_code": settings.MELHOR_ENVIO_ORIGIN_CEP,
        },
        "to": {
            "postal_code": cep,
        },
        "products": products,
        "options": {
            "receipt": False,
            "own_hand": False,
            "collect": False,
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.MELHOR_ENVIO_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Risk Clube",
    }

    try:
        response = requests.post(
            f"{base_url}/api/v2/me/shipment/calculate",
            json=payload,
            headers=headers,
            timeout=20,
        )
    except requests.RequestException:
        return JsonResponse({
            "success": False,
            "error": "Erro ao conectar com o Melhor Envio.",
        }, status=500)

    if response.status_code not in [200, 201]:
        return JsonResponse({
            "success": False,
            "error": "Erro ao calcular frete.",
            "details": response.text,
        }, status=response.status_code)

    results = response.json()
    options = []

    for option in results:
        if option.get("error"):
            continue

        option_name = (option.get("name") or "").strip()
        option_name_lower = option_name.lower()

        company_data = option.get("company") or {}
        company_name = (company_data.get("name") or "").strip()
        company_name_lower = company_name.lower()

        company_icon = (
            company_data.get("picture")
            or company_data.get("logo")
            or ""
        )

        allow_option = False

        if "sedex" in option_name_lower:
            allow_option = True
        elif "jadlog" in company_name_lower or "jadlog.com" in option_name_lower:
            allow_option = True
        elif "loggi" in company_name_lower and "express" in option_name_lower:
            allow_option = True

        if not allow_option:
            continue

        price = option.get("price") or option.get("custom_price")

        if not price:
            continue

        options.append({
            "id": str(option.get("id")),
            "name": option_name,
            "company": company_name,
            "price": float(to_decimal(price)),
            "delivery_time": option.get("delivery_time", ""),
            "cep": cep,
            "icon": company_icon,
        })

    if not options:
        return JsonResponse({
            "success": False,
            "error": "Nenhuma opção de frete disponível para esse CEP.",
        }, status=400)

    options = sorted(options, key=lambda option: option["price"])

    return JsonResponse({
        "success": True,
        "free_shipping": False,
        "options": options,
    })


@require_POST
def select_shipping(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos.",
        }, status=400)

    cart = request.session.get("cart", {})

    if not cart:
        return JsonResponse({
            "success": False,
            "error": "Carrinho vazio.",
        }, status=400)

    subtotal = get_cart_subtotal(cart)

    if subtotal >= FREE_SHIPPING_LIMIT:
        price = 0
        name = "Frete grátis"
        icon = ""
    else:
        price = float(to_decimal(data.get("price", 0)))
        name = data.get("name", "Frete")
        icon = data.get("icon", "")

        if price <= 0:
            return JsonResponse({
                "success": False,
                "error": "Frete inválido.",
            }, status=400)

    shipping = {
        "id": data.get("id"),
        "name": name,
        "company": data.get("company", ""),
        "price": price,
        "time": data.get("delivery_time", ""),
        "cep": data.get("cep", ""),
        "icon": icon,
    }

    request.session["shipping"] = shipping
    request.session.modified = True

    return JsonResponse(get_cart_payload(request))


def checkout_infinitepay(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,
        "redirect_url": f"{settings.SITE_URL}/sucesso/",
        "items": [
            {
                "quantity": 1,
                "price": money_to_cents(product.price),
                "description": product.name,
            }
        ],
    }

    response = requests.post(
        "https://api.checkout.infinitepay.io/links",
        json=payload,
        timeout=15,
    )

    if response.status_code not in [200, 201]:
        return HttpResponseBadRequest(response.text)

    data = response.json()

    return redirect(data["url"])


def checkout_infinitepay_cart(request):
    cart = request.session.get("cart", {})
    shipping = request.session.get("shipping")

    if not cart:
        return HttpResponseBadRequest("Carrinho vazio.")

    subtotal = get_cart_subtotal(cart)

    if subtotal < FREE_SHIPPING_LIMIT and not shipping:
        return HttpResponseBadRequest(
            "Selecione uma opção de frete antes de finalizar a compra."
        )

    items = []

    for cart_key, item in cart.items():
        name = item.get("name", "Produto")
        size = item.get("size", "")
        color = item.get("color", "")
        engraving_name = item.get("engraving_name", "")

        description_parts = [name]

        if color:
            description_parts.append(f"Cor: {color}")

        if size:
            description_parts.append(f"Tamanho: {size}")

        if engraving_name:
            description_parts.append(f"Gravação: {engraving_name}")

        description = " | ".join(description_parts)

        items.append({
            "quantity": int(item.get("quantity", 1)),
            "price": money_to_cents(item.get("price", 0)),
            "description": description,
        })

    if subtotal >= FREE_SHIPPING_LIMIT:
        shipping = {
            "id": "free",
            "name": "Frete grátis",
            "company": "",
            "price": 0,
            "time": "",
            "cep": shipping.get("cep", "") if shipping else "",
            "icon": "",
        }

        request.session["shipping"] = shipping
        request.session.modified = True

    if shipping:
        shipping_price = to_decimal(shipping.get("price", 0))

        if shipping_price > 0:
            shipping_description = f"Frete - {shipping.get('name', 'Entrega')}"

            if shipping.get("company"):
                shipping_description += f" | {shipping.get('company')}"

            items.append({
                "quantity": 1,
                "price": money_to_cents(shipping_price),
                "description": shipping_description,
            })

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,
        "redirect_url": f"{settings.SITE_URL}/sucesso/",
        "items": items,
    }

    response = requests.post(
        "https://api.checkout.infinitepay.io/links",
        json=payload,
        timeout=15,
    )

    if response.status_code not in [200, 201]:
        return HttpResponseBadRequest(response.text)

    data = response.json()

    return redirect(data["url"])