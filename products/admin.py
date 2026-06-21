from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Product,
    ProductImage,
    ProductVariant,
    ProductSize,
    ProductDefaultSize,
    VariantImage,
)


class ProductDefaultSizeInline(TabularInline):
    model = ProductDefaultSize
    verbose_name = "Tamanho padrão"
    verbose_name_plural = "Tamanhos padrão"
    extra = 1

    fields = (
        "name",
        "active",
    )


class ProductImageInline(TabularInline):
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
                '<img src="{}" style="width:72px;height:72px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


class ProductVariantInline(TabularInline):
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
                '<img src="{}" style="width:72px;height:72px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


class ProductSizeInline(TabularInline):
    model = ProductSize
    verbose_name = "Tamanho"
    verbose_name_plural = "Tamanhos"
    extra = 1

    fields = (
        "name",
        "active",
    )


class VariantImageInline(TabularInline):
    model = VariantImage
    verbose_name = "Imagem da variação"
    verbose_name_plural = "Imagens da variação"
    extra = 1

    fields = (
        "preview",
        "image",
        "alt",
        "active",
    )

    readonly_fields = (
        "preview",
    )

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:72px;height:72px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Prévia"


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "preview",
        "name",
        "engraving_position",
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
        "engraving_position",
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
        "back_preview",
        "created",
    )

    fieldsets = (
        ("Informações principais", {
            "fields": (
                "preview",
                "name",
                "slug",
                "price",
                "description",
            )
        }),

        ("Imagens principais", {
            "fields": (
                "image",
                "image_hover",
                "back_preview",
                "back_image",
            )
        }),

        ("Personalização", {
            "fields": (
                "engraving_position",
                "default_color_name",
                "default_color_hex",
            )
        }),

        ("Status", {
            "fields": (
                "available",
                "created",
            )
        }),
    )

    inlines = [
        ProductDefaultSizeInline,
        ProductImageInline,
        ProductVariantInline,
    ]

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:52px;height:52px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Imagem"

    def back_preview(self, obj):
        if obj and obj.back_image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.back_image.url
            )
        return "Sem imagem de costas"

    back_preview.short_description = "Prévia costas"


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    list_display = (
        "preview",
        "product",
        "color_name",
        "color_hex_badge",
        "active",
    )

    list_filter = (
        "active",
        "product",
    )

    search_fields = (
        "product__name",
        "color_name",
    )

    inlines = [
        ProductSizeInline,
        VariantImageInline,
    ]

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:52px;height:52px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Imagem"

    def color_hex_badge(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:8px;">'
            '<span style="width:18px;height:18px;border-radius:50%;background:{};border:1px solid #ccc;"></span>'
            '{}'
            '</span>',
            obj.color_hex,
            obj.color_hex,
        )

    color_hex_badge.short_description = "Cor"


@admin.register(ProductSize)
class ProductSizeAdmin(ModelAdmin):
    list_display = (
        "variant",
        "name",
        "active",
    )

    list_filter = (
        "active",
        "variant__product",
    )

    search_fields = (
        "name",
        "variant__color_name",
        "variant__product__name",
    )


@admin.register(ProductDefaultSize)
class ProductDefaultSizeAdmin(ModelAdmin):
    list_display = (
        "product",
        "name",
        "active",
    )

    list_filter = (
        "active",
        "product",
    )

    search_fields = (
        "name",
        "product__name",
    )


@admin.register(VariantImage)
class VariantImageAdmin(ModelAdmin):
    list_display = (
        "preview",
        "variant",
        "alt",
        "active",
    )

    list_filter = (
        "active",
        "variant__product",
    )

    search_fields = (
        "variant__product__name",
        "variant__color_name",
        "alt",
    )

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="width:52px;height:52px;object-fit:cover;border-radius:12px;border:1px solid #ddd;">',
                obj.image.url
            )
        return "Sem imagem"

    preview.short_description = "Imagem"