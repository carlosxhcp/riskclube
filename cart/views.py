import json
import uuid
import requests

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from products.models import Product
from orders.models import Order, OrderItem
from cart.models import Coupon


FREE_SHIPPING_LIMIT = Decimal("250.00")


def to_decimal(value, default="0.00"):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


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


def calculate_coupon_discount(coupon, subtotal):
    if subtotal <= 0:
        return Decimal("0.00")

    if coupon.discount_type == "percent":
        discount = subtotal * (coupon.discount_value / Decimal("100"))
    else:
        discount = coupon.discount_value

    return min(discount, subtotal)


def get_applied_coupons(request):
    return request.session.get("coupons", [])


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
            "custom_name": item.get("custom_name", ""),
            "engraving_side": item.get("engraving_side", ""),
            "name_direction": item.get("name_direction", ""),
            "name_font": item.get("name_font", ""),
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

    progress = min((subtotal / FREE_SHIPPING_LIMIT) * 100, 100) if FREE_SHIPPING_LIMIT > 0 else 0

    applied_coupons = get_applied_coupons(request)
    valid_session_coupons = []
    coupon_data = []
    discount = Decimal("0.00")

    for coupon_code in applied_coupons:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
        except Coupon.DoesNotExist:
            continue

        if not coupon.is_valid_now():
            continue

        if subtotal < coupon.min_order_value:
            continue

        remaining_subtotal = subtotal - discount
        coupon_discount = calculate_coupon_discount(coupon, remaining_subtotal)

        if coupon_discount <= 0:
            continue

        discount += coupon_discount
        valid_session_coupons.append(coupon.code.upper())

        coupon_data.append({
            "code": coupon.code,
            "discount": float(coupon_discount),
        })

    request.session["coupons"] = valid_session_coupons
    request.session.modified = True

    if discount > subtotal:
        discount = subtotal

    total = subtotal + shipping_price - discount

    if total < 0:
        total = Decimal("0.00")

    return {
        "success": True,
        "items": items,
        "subtotal": float(subtotal),
        "discount": float(discount),
        "coupons": coupon_data,
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
            "error": "Dados inválidos."
        }, status=400)

    product_id = data.get("product_id")

    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    size = str(data.get("size") or "Único").strip()
    color = str(data.get("color") or "").strip()
    custom_name = str(data.get("custom_name") or "").strip()[:20]
    engraving_side = str(data.get("engraving_side") or "").strip()[:20]
    name_direction = str(data.get("name_direction") or "").strip()[:20]
    name_font = str(data.get("name_font") or "").strip()[:100]

    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})

    safe_color = color.replace(" ", "-")
    safe_size = size.replace(" ", "-")
    safe_custom_name = custom_name.replace(" ", "-")
    safe_engraving_side = engraving_side.replace(" ", "-")
    safe_name_direction = name_direction.replace(" ", "-")

    cart_key = (
        f"{product.id}_"
        f"{safe_color}_"
        f"{safe_size}_"
        f"{safe_custom_name}_"
        f"{safe_engraving_side}_"
        f"{safe_name_direction}"
    )

    final_image = data.get("image") or (product.image.url if product.image else "")

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
            "custom_name": custom_name,
            "engraving_side": engraving_side,
            "name_direction": name_direction,
            "name_font": name_font,
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
        return JsonResponse({"success": False, "error": "Dados inválidos."}, status=400)

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
def apply_coupon(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos."
        }, status=400)

    code = str(data.get("code") or "").strip().upper()

    if not code:
        return JsonResponse({
            "success": False,
            "error": "Digite um cupom."
        }, status=400)

    cart = request.session.get("cart", {})

    if not cart:
        return JsonResponse({
            "success": False,
            "error": "Carrinho vazio."
        }, status=400)

    subtotal = get_cart_subtotal(cart)

    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Cupom inválido."
        }, status=404)

    if not coupon.is_valid_now():
        return JsonResponse({
            "success": False,
            "error": "Cupom expirado ou inativo."
        }, status=400)

    if subtotal < coupon.min_order_value:
        return JsonResponse({
            "success": False,
            "error": f"Pedido mínimo de R$ {coupon.min_order_value}."
        }, status=400)

    coupons = request.session.get("coupons", [])

    if len(coupons) >= 2:
        return JsonResponse({
            "success": False,
            "error": "Você pode utilizar no máximo 2 cupons por compra."
        }, status=400)

    if coupon.code.upper() in [c.upper() for c in coupons]:
        return JsonResponse({
            "success": False,
            "error": "Este cupom já foi aplicado."
        }, status=400)

    coupons.append(coupon.code.upper())

    request.session["coupons"] = coupons
    request.session.modified = True

    return JsonResponse(get_cart_payload(request))


@require_POST
def remove_coupon(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos."
        }, status=400)

    code = str(data.get("code") or "").strip().upper()

    coupons = request.session.get("coupons", [])

    coupons = [
        coupon_code for coupon_code in coupons
        if coupon_code.upper() != code
    ]

    request.session["coupons"] = coupons
    request.session.modified = True

    return JsonResponse(get_cart_payload(request))


@require_POST
def calculate_shipping(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Dados inválidos."}, status=400)

    cep = str(data.get("cep", "")).replace("-", "").replace(".", "").strip()
    cart = request.session.get("cart", {})

    if not cep or len(cep) != 8 or not cep.isdigit():
        return JsonResponse({"success": False, "error": "CEP inválido."}, status=400)

    if not cart:
        return JsonResponse({"success": False, "error": "Carrinho vazio."}, status=400)

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
            "options": [{
                "id": "free",
                "name": "Frete grátis",
                "company": "",
                "price": 0,
                "delivery_time": "",
                "cep": cep,
                "icon": "",
            }],
        })

    for setting_name in ["MELHOR_ENVIO_TOKEN", "MELHOR_ENVIO_ORIGIN_CEP"]:
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
        "from": {"postal_code": settings.MELHOR_ENVIO_ORIGIN_CEP},
        "to": {"postal_code": cep},
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

        search_text = f"{company_name_lower} {option_name_lower}"

        is_loggi_express = (
            "loggi" in search_text
            and "express" in search_text
        )

        is_correios = (
            "correios" in search_text
            or "sedex" in search_text
            or "pac" in search_text
        )

        if not (is_loggi_express or is_correios):
            continue

        price = option.get("price") or option.get("custom_price")

        if not price:
            continue

        company_icon = (
            company_data.get("picture")
            or company_data.get("logo")
            or ""
        )

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
        return JsonResponse({"success": False, "error": "Dados inválidos."}, status=400)

    cart = request.session.get("cart", {})

    if not cart:
        return JsonResponse({"success": False, "error": "Carrinho vazio."}, status=400)

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
            return JsonResponse({"success": False, "error": "Frete inválido."}, status=400)

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


def get_mercadopago_headers():
    return {
        "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4()),
    }


def update_order_payment_status(order, payment_data):
    status = payment_data.get("status", "")
    payment_id = str(payment_data.get("id", ""))

    if status == "approved":
        order.status = "paid"
        order.paid_at = timezone.now()
    elif status in ["rejected", "cancelled"]:
        order.status = "cancelled"
    else:
        order.status = "pending"

    if hasattr(order, "mercadopago_payment_id"):
        order.mercadopago_payment_id = payment_id

    order.save()


def create_order_from_cart(request, email):
    cart = request.session.get("cart", {})
    shipping = request.session.get("shipping")

    if not cart:
        return None, "Carrinho vazio."

    subtotal = get_cart_subtotal(cart)

    if subtotal < FREE_SHIPPING_LIMIT and not shipping:
        return None, "Selecione uma opção de frete antes de finalizar a compra."

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

    payload_cart = get_cart_payload(request)

    shipping_price = to_decimal(payload_cart.get("shipping_price", 0))
    discount = to_decimal(payload_cart.get("discount", 0))
    total = subtotal + shipping_price - discount

    if total <= 0:
        return None, "O total do pedido precisa ser maior que zero."

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        email=email,
        status="pending",
        subtotal=subtotal,
        shipping_price=shipping_price,
        discount=discount,
        total=total,
    )

    for cart_key, item in cart.items():
        quantity = int(item.get("quantity", 1))
        price = to_decimal(item.get("price", 0))
        item_subtotal = price * quantity

        OrderItem.objects.create(
            order=order,
            product_id=item.get("product_id"),
            name=item.get("name", "Produto"),
            size=item.get("size", ""),
            color=item.get("color", ""),
            custom_name=item.get("custom_name", ""),
            engraving_side=item.get("engraving_side", ""),
            name_direction=item.get("name_direction", ""),
            name_font=item.get("name_font", ""),
            quantity=quantity,
            price=price,
            subtotal=item_subtotal,
            image=item.get("image", ""),
        )

    return order, None


@require_POST
def checkout_mercadopago_cart(request):
    if not getattr(settings, "MP_ACCESS_TOKEN", None):
        return JsonResponse({
            "success": False,
            "error": "MP_ACCESS_TOKEN não configurado."
        }, status=500)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Dados inválidos."
        }, status=400)

    email = str(data.get("email") or "").strip().lower()

    if not email:
        return JsonResponse({
            "success": False,
            "error": "Informe seu e-mail."
        }, status=400)

    payment_type = str(data.get("payment_type") or "pix").strip().lower()

    order, error = create_order_from_cart(request, email)

    if error:
        return JsonResponse({
            "success": False,
            "error": error
        }, status=400)

    payment_data = {
        "transaction_amount": float(order.total),
        "description": f"Pedido Risk Clube #{order.id}",
        "external_reference": str(order.id),
        "payer": {
            "email": email
        },
    }

    if payment_type == "pix":
        payment_data["payment_method_id"] = "pix"

    elif payment_type == "card":
        token = data.get("token")
        payment_method_id = data.get("payment_method_id")

        try:
            installments = int(data.get("installments", 1))
        except (TypeError, ValueError):
            installments = 1

        if not token or not payment_method_id:
            order.status = "cancelled"
            order.save()

            return JsonResponse({
                "success": False,
                "error": "Dados do cartão inválidos."
            }, status=400)

        payer_email = data.get("payer_email") or email

        payer = {
            "email": payer_email
        }

        identification_type = data.get("identification_type")
        identification_number = data.get("identification_number")

        if identification_type and identification_number:
            payer["identification"] = {
                "type": identification_type,
                "number": identification_number
            }

        payment_data.update({
            "token": token,
            "payment_method_id": payment_method_id,
            "installments": installments,
            "payer": payer,
        })

        issuer_id = data.get("issuer_id")

        if issuer_id:
            payment_data["issuer_id"] = issuer_id

    else:
        order.status = "cancelled"
        order.save()

        return JsonResponse({
            "success": False,
            "error": "Forma de pagamento inválida."
        }, status=400)

    try:
        mp_response = requests.post(
            "https://api.mercadopago.com/v1/payments",
            json=payment_data,
            headers=get_mercadopago_headers(),
            timeout=30,
        )

        try:
            response = mp_response.json()
        except ValueError:
            response = {
                "message": mp_response.text
            }

    except requests.RequestException as error:
        order.status = "cancelled"
        order.save()

        return JsonResponse({
            "success": False,
            "error": "Erro ao conectar com o Mercado Pago.",
            "details": str(error),
        }, status=500)

    if mp_response.status_code not in [200, 201]:
        order.status = "cancelled"
        order.save()

        return JsonResponse({
            "success": False,
            "error": "Erro ao criar pagamento.",
            "mercadopago_status": mp_response.status_code,
            "details": response,
        }, status=400)

    update_order_payment_status(order, response)

    if response.get("status") == "approved":
        request.session.pop("cart", None)
        request.session.pop("shipping", None)
        request.session.pop("coupons", None)
        request.session.modified = True

    pix_data = response.get("point_of_interaction", {}).get("transaction_data", {})

    return JsonResponse({
        "success": True,
        "order_id": order.id,
        "status": response.get("status"),
        "payment_id": response.get("id"),
        "payment_type": payment_type,
        "pix_qr_code": pix_data.get("qr_code"),
        "pix_qr_code_base64": pix_data.get("qr_code_base64"),
        "ticket_url": pix_data.get("ticket_url"),
    })

@csrf_exempt
def mercadopago_webhook(request):
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"success": False}, status=405)

    payment_id = (
        request.GET.get("data.id")
        or request.GET.get("id")
        or request.GET.get("payment_id")
    )

    if not payment_id:
        try:
            data = json.loads(request.body or "{}")
            payment_id = (
                data.get("data", {}).get("id")
                or data.get("id")
                or data.get("payment_id")
            )
        except json.JSONDecodeError:
            payment_id = None

    if not payment_id:
        return JsonResponse({"success": True})

    try:
        mp_response = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers=get_mercadopago_headers(),
            timeout=30,
        )

        try:
            payment_data = mp_response.json()
        except ValueError:
            payment_data = {}

    except requests.RequestException:
        return JsonResponse({"success": True})

    order_id = payment_data.get("external_reference")

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            update_order_payment_status(order, payment_data)
        except Order.DoesNotExist:
            pass

    return JsonResponse({"success": True})


def checkout_page(request):
    payload = get_cart_payload(request)

    if not payload["items"]:
        return redirect("/")

    return render(request, "cart/checkout.html", {
        "cart": payload,
        "mp_public_key": settings.MP_PUBLIC_KEY,
    })
