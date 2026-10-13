import base64
import json

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from products.models import Product

from .models import CategoriaGravacao, BottleCustomization

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST





def data_url_to_file(data_url, filename):
    header, encoded = data_url.split(",", 1)
    return ContentFile(base64.b64decode(encoded), name=filename)


def createbottle_choose_type(request):
    return render(
        request,
        "customization/createbottle_choose_type.html"
    )


def createbottle_choose_model(request, custom_type):
    if custom_type not in ["individual", "grupo"]:
        return redirect(
            "customization:createbottle_choose_type"
        )

    request.session["createbottle"] = {
        "custom_type": custom_type,
    }

    request.session.modified = True

    products = Product.objects.filter(
        available=True,
        is_createbottle=True
    ).order_by("-created")

    if custom_type == "grupo":
        return render(
            request,
            "customization/createbottle_group.html",
            {
                "custom_type": custom_type,
                "products": products,
            }
        )

    return render(
        request,
        "customization/createbottle_choose_model.html",
        {
            "custom_type": custom_type,
            "products": products,
        }
    )


@ensure_csrf_cookie
def createbottle_mockup(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True,
        is_createbottle=True
    )

    categorias = CategoriaGravacao.objects.filter(
        ativo=True
    ).prefetch_related("gravacoes")

    return render(request, "customization/createbottle_mockup.html", {
        "product": product,
        "categorias": categorias,
    })
def createbottle_group_mockup(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True,
        is_createbottle=True
    )

    return render(
        request,
        "customization/createbottle_group_mockup.html",
        {
            "product": product,
        }
    )


def createbottle_group_summary(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True,
        is_createbottle=True
    )

    return render(
        request,
        "customization/createbottle_group_summary.html",
        {
            "product": product,
        }
    )

@require_POST
def save_bottle_customization(request):
    try:
        data = json.loads(request.body)
        product = get_object_or_404(Product, pk=data["product_id"])

        customization = BottleCustomization(
            product=product,
            name=data.get("name", ""),
            font=data.get("font", ""),
            layers=data.get("layers", []),
        )

        customization.texture = data_url_to_file(data["texture"], "texture.png")

        if data.get("preview"):
            customization.preview = data_url_to_file(data["preview"], "preview.jpg")

        customization.save()

        return JsonResponse({"success": True, "customization_id": str(customization.id)})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)