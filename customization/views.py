from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from .models import VipBottleModel, CategoriaGravacao


def vip_choose_type(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True, is_vip=True)

    request.session["vip_custom"] = {
        "product_id": product.id,
    }

    return render(request, "customization/vip_choose_type.html", {
        "product": product,
    })


def vip_choose_model(request, slug, custom_type):
    product = get_object_or_404(Product, slug=slug, available=True, is_vip=True)

    if custom_type not in ["individual", "grupo"]:
        return redirect("customization:vip_choose_type", slug=product.slug)

    vip_custom = request.session.get("vip_custom", {})
    vip_custom["product_id"] = product.id
    vip_custom["custom_type"] = custom_type
    request.session["vip_custom"] = vip_custom
    request.session.modified = True

    models = VipBottleModel.objects.filter(product=product, is_active=True)

    if custom_type == "grupo":
        return render(request, "customization/vip_group.html", {
            "product": product,
            "custom_type": custom_type,
            "models": models,
        })

    return render(request, "customization/vip_choose_model.html", {
        "product": product,
        "custom_type": custom_type,
        "models": models,
    })


def vip_individual_mockup(request, slug, model_id):
    product = get_object_or_404(Product, slug=slug, available=True, is_vip=True)

    bottle_model = get_object_or_404(
        VipBottleModel,
        id=model_id,
        product=product,
        is_active=True
    )

    categorias = CategoriaGravacao.objects.filter(
        ativo=True
    ).prefetch_related("gravacoes")

    return render(request, "customization/vip_individual_mockup.html", {
        "product": product,
        "bottle_model": bottle_model,
        "categorias": categorias,
    })


def vip_group_mockup(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True, is_vip=True)

    model_id = request.GET.get("model_id")
    bottle_model = None

    if model_id:
        bottle_model = get_object_or_404(
            VipBottleModel,
            id=model_id,
            product=product,
            is_active=True
        )

        vip_custom = request.session.get("vip_custom", {})
        vip_custom["product_id"] = product.id
        vip_custom["custom_type"] = "grupo"
        vip_custom["model_id"] = bottle_model.id
        request.session["vip_custom"] = vip_custom
        request.session.modified = True

    return render(request, "customization/vip_group_mockup.html", {
        "product": product,
        "bottle_model": bottle_model,
    })


def vip_group_summary(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True, is_vip=True)

    return render(request, "customization/vip_group_summary.html", {
        "product": product,
    })