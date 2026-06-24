import stripe

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product, Favorite
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

    is_favorited = False

    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            product=product
        ).exists()

    return render(request, "products/product_detail.html", {
        "product": product,
        "community_images": community_images,
        "is_favorited": is_favorited,
    })


@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        favorite.delete()
        return JsonResponse({
            "success": True,
            "favorited": False
        })

    return JsonResponse({
        "success": True,
        "favorited": True
    })



def customization_choice(request):
    return render(request, "products/customization_choice.html")

@login_required
def toggle_favorite(request, pk):
    product = Product.objects.get(pk=pk)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        favorite.delete()
        return JsonResponse({"favorited": False})

    return JsonResponse({"favorited": True})