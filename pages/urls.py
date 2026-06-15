from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("trocas/", views.trocas, name="trocas"),
    path("contato/", views.contato, name="contato"),
    path("about/", views.about, name="about"),
    path("newsletter/", views.newsletter_signup, name="newsletter_signup"),
]