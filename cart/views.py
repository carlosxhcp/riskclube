import requests

from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseBadRequest

from products.models import Product


def checkout_infinitepay(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,

        "redirect_url": f"{settings.SITE_URL}/sucesso/",

        "items": [
            {
                "quantity": 1,

                # preço em centavos
                "price": int(product.price * 100),

                # nome automático
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