from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Product,
    ProductImage,
    ProductVariant,
    CommunityImage,
    EngravingMockup,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    verbose_name = "Imagem"
    verbose_name_plural = "Imagens do produto"
    extra = 1
    fields = ("preview", "image", "alt")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    verbose_name = "Cor"
    verbose_name_plural = "Variações de cor"
    extra = 1
    fields = ("preview", "color_name", "color_hex", "image", "active")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


class EngravingMockupInline(admin.TabularInline):
    model = EngravingMockup
    verbose_name = "Gravação"
    verbose_name_plural = "Gravações"
    extra = 1

    fields = (
        "variant",
        "name",
        "thumbnail_preview",
        "thumbnail",
        "main_image_preview",
        "main_image",
        "active",
    )

    readonly_fields = (
        "thumbnail_preview",
        "main_image_preview",
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "variant":
            product_id = request.resolver_match.kwargs.get("object_id")

            if product_id:
                kwargs["queryset"] = ProductVariant.objects.filter(
                    product_id=product_id,
                    active=True
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def thumbnail_preview(self, obj):
        if obj and obj.thumbnail:
            return format_html(
                '<img src="{}" style="width:70px;height:70px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">',
                obj.thumbnail.url
            )
        return "Sem miniatura"

    thumbnail_preview.short_description = "Miniatura"

    def main_image_preview(self, obj):
        if obj and obj.main_image:
            return format_html(
                '<img src="{}" style="width:90px;height:90px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">',
                obj.main_image.url
            )
        return "Sem imagem"

    main_image_preview.short_description = "Imagem da galeria"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "name",
        "price",
        "available",
        "is_vip",
    )

    list_filter = (
        "available",
        "is_vip",
    )

    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("1. Informações principais", {
            "fields": (
                "name",
                "slug",
                "price",
                "description",
            )
        }),

        ("2. Status do produto", {
            "fields": (
                "available",
                "is_vip",
            )
        }),

        ("3. Cor principal", {
            "fields": (
                "default_color_name",
                "default_color_hex",
                "image",
                "image_hover",
            )
        }),
    )

    inlines = [
        ProductImageInline,
        ProductVariantInline,
        EngravingMockupInline,
    ]

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:cover;border-radius:8px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


@admin.register(CommunityImage)
class CommunityImageAdmin(admin.ModelAdmin):
    list_display = ("preview", "alt", "active")
    list_filter = ("active",)
    fields = ("preview", "image", "alt", "active")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:90px;height:90px;object-fit:cover;border-radius:10px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"