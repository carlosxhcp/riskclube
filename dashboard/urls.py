from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("produtos/", views.products_list, name="products_list"),
    path("produtos/<int:pk>/editar/", views.product_edit, name="product_edit"),
    path("variacoes/<int:pk>/editar/", views.variant_edit, name="variant_edit"),
    path("produtos/<int:pk>/variacoes/nova/", views.variant_create, name="variant_create"),

    path("variacoes/<int:pk>/tamanhos/novo/", views.size_create, name="size_create"),
    path("tamanhos/<int:pk>/editar/", views.size_edit, name="size_edit"),
    path("tamanhos/<int:pk>/excluir/", views.size_delete, name="size_delete"),
    path("produtos/<int:pk>/tamanhos/novo/", views.product_size_create, name="product_size_create"),
path("produtos/tamanhos/<int:pk>/editar/", views.product_size_edit, name="product_size_edit"),
path("produtos/tamanhos/<int:pk>/excluir/", views.product_size_delete, name="product_size_delete"),
]