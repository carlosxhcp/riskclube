from django.shortcuts import render, get_object_or_404
from .models import Product, CommunityImage


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    community_images = CommunityImage.objects.filter(active=True)[:10]

    return render(request, "products/product_detail.html", {
        "product": product,
        "community_images": community_images,
    })