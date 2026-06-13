from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def minha_conta(request):
    orders = request.user.orders.prefetch_related("items").all()

    return render(request, "accounts/minha_conta.html", {
        "orders": orders,
    })