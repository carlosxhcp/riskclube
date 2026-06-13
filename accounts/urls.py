from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("minha-conta/", views.minha_conta, name="minha_conta"),
]