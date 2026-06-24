from django.urls import path
from . import views

app_name = "customization"

urlpatterns = [
    path(
        "personalizar/",
        views.createbottle_choose_type,
        name="createbottle_choose_type"
    ),

    path(
        "personalizar/<str:custom_type>/modelos/",
        views.createbottle_choose_model,
        name="createbottle_choose_model"
    ),

    path(
        "personalizar/<slug:slug>/mockup/",
        views.createbottle_mockup,
        name="createbottle_mockup"
    ),

    path(
        "personalizar/<slug:slug>/grupo/",
        views.createbottle_group_mockup,
        name="createbottle_group_mockup"
    ),

    path(
        "personalizar/<slug:slug>/grupo/resumo/",
        views.createbottle_group_summary,
        name="createbottle_group_summary"
    ),
]