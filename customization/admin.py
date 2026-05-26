from django.contrib import admin
from .models import VipBottleModel


@admin.register(VipBottleModel)
class VipBottleModelAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "active", "order")
    list_filter = ("active", "product")
    search_fields = ("name", "product__name")
    list_editable = ("active", "order")