from django.shortcuts import render
from products.models import Product


def home(request):
    products = Product.objects.filter(available=True)

    return render(request, "pages/home.html", {
        "products": products
    })