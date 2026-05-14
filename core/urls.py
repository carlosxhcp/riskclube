from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("", include("products.urls")),
    path("", include("cart.urls")),
    path(
    "produto/<slug:slug>/checkout/",
    views.checkout_stripe_product,
    name="checkout_stripe_product"
),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)