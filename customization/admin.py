from django.contrib import admin
from django.utils.html import format_html
from .models import VipBottleModel, CategoriaGravacao, Gravacao


@admin.register(VipBottleModel)
class VipBottleModelAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "is_active", "preview")
    list_filter = ("is_active",)
    search_fields = ("name", "product__name")

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:contain;border-radius:6px;" />',
                obj.image.url
            )
        return "-"

    preview.short_description = "Imagem"


class GravacaoInline(admin.TabularInline):
    model = Gravacao
    extra = 1
    fields = ("nome", "imagem", "preview", "ativo", "ordem")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:contain;border-radius:6px;" />',
                obj.imagem.url
            )
        return "-"

    preview.short_description = "Prévia"


@admin.register(CategoriaGravacao)
class CategoriaGravacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "ordem", "preview_icone")
    list_editable = ("ativo", "ordem")
    search_fields = ("nome",)
    inlines = [GravacaoInline]

    def preview_icone(self, obj):
        if obj.icone:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:contain;border-radius:6px;" />',
                obj.icone.url
            )
        return "-"

    preview_icone.short_description = "Ícone"


@admin.register(Gravacao)
class GravacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "ativo", "ordem", "preview")
    list_filter = ("categoria", "ativo")
    list_editable = ("ativo", "ordem")
    search_fields = ("nome", "categoria__nome")

    def preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="width:55px;height:55px;object-fit:contain;border-radius:6px;" />',
                obj.imagem.url
            )
        return "-"

    preview.short_description = "Imagem"


