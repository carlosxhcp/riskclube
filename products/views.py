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


def checkout_stripe_product(request, slug):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    product = get_object_or_404(
        Product,
        slug=slug,
        available=True
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "brl",
                    "product_data": {
                        "name": product.name,
                    },
                    "unit_amount": int(product.price * 100),
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.SITE_URL}/produto/{product.slug}/?payment=success",
        cancel_url=f"{settings.SITE_URL}/produto/{product.slug}/?payment=cancel",
    )

    return redirect(session.url)


def customization_choice(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        available=True
    )

    return render(request, "products/customization_choice.html", {
        "product": product,
    })