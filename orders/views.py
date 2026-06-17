from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Order


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, "orders/order_success.html", {
        "order": order
    })


def order_pix(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, "orders/order_pix.html", {
        "order": order
    })


def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return JsonResponse({
        "status": order.status
    })