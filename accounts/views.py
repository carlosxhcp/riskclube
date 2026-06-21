from django.contrib.auth.decorators import login_required

from orders.models import Order
from products.models import Favorite
from django.shortcuts import render, get_object_or_404


@login_required
def minha_conta(request):
    orders = Order.objects.filter(
        email=request.user.email
    ).prefetch_related("items").order_by("-created_at")

    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related("product").order_by("-created_at")

    return render(request, "accounts/minha_conta.html", {
        "orders": orders,
        "favorites": favorites,
    })