import base64
import json

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from products.models import Product

from .models import CategoriaGravacao, BottleCustomization


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

    return render(
        request,
        "customization/createbottle_mockup.html",
        {
            "product": product,
            "categorias": categorias,
        }
    )


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


def save_bottle_customization(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Método não permitido."
            },
            status=405
        )

    try:
        data = json.loads(request.body)

        product_id = data.get("product_id")
        name = data.get("name", "").strip()
        font = data.get("font", "").strip()
        layers = data.get("layers", [])
        texture_data = data.get("texture")

        if not product_id:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Produto não informado."
                },
                status=400
            )

        product = get_object_or_404(
            Product,
            id=product_id,
            available=True,
            is_createbottle=True
        )

        if len(name) > 15:
            return JsonResponse(
                {
                    "success": False,
                    "message": "O nome pode ter no máximo 15 caracteres."
                },
                status=400
            )

        configuration = {
            "layers": layers,
        }

        customization = BottleCustomization.objects.create(
            product=product,
            name=name,
            font=font,
            configuration=configuration,
        )

        if texture_data:
            try:
                header, encoded_data = texture_data.split(
                    ",",
                    1
                )

                image_data = base64.b64decode(
                    encoded_data
                )

                file_name = (
                    f"customization_{customization.id}.png"
                )

                customization.texture_image.save(
                    file_name,
                    ContentFile(image_data),
                    save=True
                )

            except (ValueError, TypeError):
                customization.delete()

                return JsonResponse(
                    {
                        "success": False,
                        "message": "A textura enviada é inválida."
                    },
                    status=400
                )

        return JsonResponse(
            {
                "success": True,
                "customization_id": customization.id,
                "message": "Personalização salva com sucesso."
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Dados JSON inválidos."
            },
            status=400
        )

    except Exception as error:
        return JsonResponse(
            {
                "success": False,
                "message": str(error)
            },
            status=500
        )
