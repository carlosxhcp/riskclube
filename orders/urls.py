from django.urls import path
from . import views

urlpatterns = [
    path("pedido/<int:order_id>/sucesso/", views.order_success, name="order_success"),
    path("pedido/<int:order_id>/pix/", views.order_pix, name="order_pix"),
    path("pedido/<int:order_id>/status/", views.order_status, name="order_status"),
]