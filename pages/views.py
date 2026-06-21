from django.shortcuts import render
from products.models import Product
from .models import CommunityReview


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings

from .models import NewsletterLead

from orders.models import Order

def home(request):
    query = request.GET.get("q")

    products = Product.objects.filter(available=True)

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

def trocas(request):
    return render(request, "pages/trocas.html")

def contato(request):
    return render(request, "pages/contato.html")

def about(request):
    return render(request, "pages/about.html")

@require_POST
def newsletter_signup(request):
    email = request.POST.get("email", "").strip().lower()
    coupon_code = "RISK15"

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Digite um e-mail válido."
        }, status=400)

    lead, created = NewsletterLead.objects.get_or_create(
        email=email,
        defaults={
            "coupon_code": coupon_code
        }
    )

    if not created:
        return JsonResponse({
            "success": False,
            "message": "Este e-mail já recebeu um cupom."
        }, status=400)

    try:
        send_mail(
            subject="Seu cupom Risk Clube chegou!",
            message=f"Use o cupom {coupon_code} e ganhe R$15 de desconto na sua compra.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as error:
        print("ERRO AO ENVIAR EMAIL:", error)

        return JsonResponse({
            "success": True,
            "message": "E-mail salvo! Configure o envio de e-mails para entregar o cupom."
        })

    return JsonResponse({
        "success": True,
        "message": "Cupom enviado para seu e-mail!"
    })
