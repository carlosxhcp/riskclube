import requests
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import json


def money_to_cents(value):
    return int(Decimal(str(value)) * 100)


def checkout_infinitepay(request):
    cart = request.session.get("cart", {})

    if not cart:
        return HttpResponseBadRequest("Carrinho vazio.")

    if not settings.INFINITEPAY_HANDLE:
        return HttpResponseBadRequest("INFINITEPAY_HANDLE não configurado.")

    # Aqui você pode trocar depois pelo ID real do seu Order
    order_nsu = f"pedido-{request.session.session_key}"

    items = []

    for cart_key, item in cart.items():
        name = item.get("name", "Produto")
        size = item.get("size", "")

        items.append({
            "quantity": int(item.get("quantity", 1)),
            "price": money_to_cents(item.get("price", 0)),
            "description": f"{name} - Tam. {size}",
        })

    shipping = request.session.get("shipping", {})
    shipping_price = Decimal(str(shipping.get("price", 0)))

    if shipping_price > 0:
        items.append({
            "quantity": 1,
            "price": money_to_cents(shipping_price),
            "description": "Frete",
        })

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,
        "redirect_url": f"{settings.SITE_URL}/cart/infinitepay/retorno/",
        "webhook_url": f"{settings.SITE_URL}/cart/infinitepay/webhook/",
        "order_nsu": order_nsu,
        "items": items,
    }

    response = requests.post(
        "https://api.checkout.infinitepay.io/links",
        json=payload,
        timeout=15
    )

    if response.status_code not in [200, 201]:
        return HttpResponseBadRequest(f"Erro InfinitePay: {response.text}")

    data = response.json()
    payment_url = data.get("url")

    if not payment_url:
        return HttpResponseBadRequest("A InfinitePay não retornou o link de pagamento.")

    return redirect(payment_url)


def infinitepay_return(request):
    return JsonResponse({
        "message": "Retorno InfinitePay recebido.",
        "order_nsu": request.GET.get("order_nsu"),
        "transaction_nsu": request.GET.get("transaction_nsu"),
        "slug": request.GET.get("slug"),
        "capture_method": request.GET.get("capture_method"),
        "receipt_url": request.GET.get("receipt_url"),
    })


@csrf_exempt
def infinitepay_webhook(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Método inválido"}, status=400)

    try:
        data = json.loads(request.body)
        print("=== WEBHOOK INFINITEPAY ===")
        print(data)

        order_nsu = data.get("order_nsu")
        transaction_nsu = data.get("transaction_nsu")
        receipt_url = data.get("receipt_url")
        capture_method = data.get("capture_method")
        installments = data.get("installments")

        # Aqui depois você vai buscar seu Order pelo order_nsu
        # order = Order.objects.filter(infinitepay_order_nsu=order_nsu).first()
        # order.status = "paid"
        # order.infinitepay_transaction_nsu = transaction_nsu
        # order.receipt_url = receipt_url
        # order.save()

        return JsonResponse({
            "success": True,
            "message": None
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)