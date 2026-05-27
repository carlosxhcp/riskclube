from django.urls import path
from . import views

app_name = "customization"

urlpatterns = [
    path(
        "produto/<slug:slug>/personalizar/",
        views.vip_choose_type,
        name="vip_choose_type"
    ),
    path(
        "produto/<slug:slug>/personalizar/<str:custom_type>/modelos/",
        views.vip_choose_model,
        name="vip_choose_model"
    ),
    path(
    "vip/<slug:slug>/grupo/mockup/",
    views.vip_group_mockup,
    name="vip_group_mockup"
    ),
]