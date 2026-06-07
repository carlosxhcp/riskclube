from django.shortcuts import render
from products.models import Product
from .models import CommunityReview


from .models import CommunityReview

def home(request):
    categorias = [
        {
            "slug": "termicas",
            "nome": "Térmicas",
        },
        {
            "slug": "squeeze",
            "nome": "Squeeze",
        },
        {
            "slug": "personalizadas",
            "nome": "Personalizadas",
        },
    ]

    categoria_atual = request.GET.get("categoria", "termicas")
    query = request.GET.get("q")

    products = Product.objects.filter(available=True)

    if categoria_atual:
        products = products.filter(category=categoria_atual)

    if query:
        products = products.filter(name__icontains=query)

    community_images = CommunityReview.objects.all().order_by("-id")

    return render(request, "pages/home.html", {
        "products": products,
        "query": query,
        "categorias": categorias,
        "categoria_atual": categoria_atual,
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

def trocas(request):
    return render(request, "pages/trocas.html")

def contato(request):
    return render(request, "pages/contato.html")

def about(request):
    return render(request, "pages/about.html")