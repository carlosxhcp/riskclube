from django.contrib import admin
from .models import Product, ProductImage, CommunityImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "available", "created")
    list_filter = ("available", "created")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]



@admin.register(CommunityImage)
class CommunityImageAdmin(admin.ModelAdmin):
    list_display = ("alt", "active", "created")
    list_filter = ("active", "created")
    search_fields = ("alt",)