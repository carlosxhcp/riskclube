from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Product,
    ProductImage,
    ProductVariant,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    verbose_name = "Imagem extra"
    verbose_name_plural = "Imagens extras"
    extra = 1

    fields = (
        "preview",
        "image",
        "alt",
    )

    readonly_fields = (
        "preview",
    )

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    verbose_name = "Variação de cor"
    verbose_name_plural = "Variações de cor"
    extra = 1

    fields = (
        "preview",
        "color_name",
        "color_hex",
        "image",
        "active",
    )

    readonly_fields = (
        "preview",
    )

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "name",
        "category",
        "price",
        "available",
        "created",
    )

    list_display_links = (
        "preview",
        "name",
    )

    list_filter = (
        "available",
        "category",
        "created",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    readonly_fields = (
        "preview",
        "created",
    )

    fieldsets = (
        ("1. Informações principais", {
            "fields": (
                "preview",
                "name",
                "slug",
                "category",
                "price",
                "description",
            )
        }),

        ("2. Imagens principais", {
            "fields": (
                "image",
                "image_hover",
            )
        }),

        ("3. Cor principal", {
            "fields": (
                "default_color_name",
                "default_color_hex",
            )
        }),

        ("4. Status", {
            "fields": (
                "available",
                "created",
            )
        }),
    )

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"