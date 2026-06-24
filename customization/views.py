from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from .models import CategoriaGravacao


def createbottle_choose_type(request):
    return render(request, "customization/createbottle_choose_type.html")


def createbottle_choose_model(request, custom_type):
    if custom_type not in ["individual", "grupo"]:
        return redirect("customization:createbottle_choose_type")

    request.session["createbottle"] = {
        "custom_type": custom_type,
    }
    request.session.modified = True

    products = Product.objects.filter(
        available=True,
        is_createbottle=True
    ).order_by("-created")

    if custom_type == "grupo":
        return render(request, "customization/createbottle_group.html", {
            "custom_type": custom_type,
            "products": products,
        })

    return render(request, "customization/createbottle_choose_model.html", {
        "custom_type": custom_type,
        "products": products,
    })


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

    return render(request, "customization/createbottle_group_mockup.html", {
        "product": product,
    })


def createbottle_group_summary(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True,
        is_createbottle=True
    )

    return render(request, "customization/createbottle_group_summary.html", {
        "product": product,
    })