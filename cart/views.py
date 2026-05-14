# views.py
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest


def checkout_infinitepay(request):

    payload = {
        "handle": settings.INFINITEPAY_HANDLE,

        "redirect_url": f"{settings.SITE_URL}/sucesso/",

        "items": [
            {
                "quantity": 1,
                "price": 1000,  # R$10,00 em centavos
                "description": "Teste InfinitePay"
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