from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("trocas/", views.trocas, name="trocas"),
    path("contato/", views.contato, name="contato"),
    path("about/", views.about, name="about"),
    path(
    "sucesso/",
    views.checkout_success,
    name="checkout_success"
),
]