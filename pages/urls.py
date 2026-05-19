from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("mockup-3d/", views.mockup_3d, name="mockup_3d"),
]