from django.shortcuts import render
from products.models import Product
from .models import CommunityReview


from .models import CommunityReview

def home(request):
    products = Product.objects.filter(available=True)

    query = request.GET.get("q")

    if query:
        products = products.filter(name__icontains=query)

    community_images = CommunityReview.objects.all().order_by("-id")

    return render(request, "pages/home.html", {
        "products": products,
        "query": query,
        "community_images": community_images,
    })


def shop(request):
    products = Product.objects.filter(available=True)

    query = request.GET.get("q")

    if query:
        products = products.filter(name__icontains=query)

    return render(request, "products/shop.html", {
        "products": products,
        "query": query,
    })


def mockup_3d(request):
    return render(request, "mockup_3d.html")