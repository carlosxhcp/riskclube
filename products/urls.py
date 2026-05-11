from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("produto/<slug:slug>/", views.product_detail, name="product_detail"),
]