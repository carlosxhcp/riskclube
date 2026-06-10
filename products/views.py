import stripe

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect

from .models import Product
from pages.models import CommunityReview


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related(
            "images",
            "variants",
            "variants__images",
            "variants__sizes",
        ),
        slug=slug,
        available=True
    )

    community_images = CommunityReview.objects.all().order_by("-id")

    return render(request, "products/product_detail.html", {
        "product": product,
        "community_images": community_images,
    })


def customization_choice(request):
    product = get_object_or_404(
        Product,
        available=True
    )

    return render(request, "products/customization_choice.html", {
        "product": product,
    })