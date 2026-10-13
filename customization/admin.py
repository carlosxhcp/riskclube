from django.contrib import admin
from django.utils.html import format_html
from .models import VipBottleModel, CategoriaGravacao, Gravacao, BottleCustomization



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




@admin.register(BottleCustomization)
class BottleCustomizationAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "font", "created_at")
    readonly_fields = ("texture_view", "preview_view", "layers_view", "created_at")
    fields = ("product", "name", "font", "preview_view", "texture_view", "layers_view", "created_at")

    def preview_view(self, obj):
        if not obj.preview:
            return "-"
        return format_html('<img src="{}" style="max-width:420px">', obj.preview.url)
    preview_view.short_description = "Foto do 3D"

    def texture_view(self, obj):
        if not obj.texture:
            return "-"
        # fundo escuro: as gravações são brancas/transparentes
        return format_html(
            '<div style="background:#444;padding:8px;display:inline-block">'
            '<img src="{0}" style="max-width:420px"></div><br>'
            '<a href="{0}" download>Baixar PNG da textura</a>',
            obj.texture.url,
        )
    texture_view.short_description = "Textura (PNG)"

    def layers_view(self, obj):
        rows = []
        for i, l in enumerate(obj.layers, 1):
            if l.get("type") == "name":
                what = f'Nome "{l.get("text")}" — fonte {l.get("font")}'
            else:
                what = f'Gravação "{l.get("name")}"'
            rows.append(
                f'{i}. {what} | x={round(l.get("x", 0))} y={round(l.get("y", 0))} '
                f'tamanho={round(l.get("size", 0))}'
            )
        return format_html("<br>".join(["{}"] * len(rows)), *rows) if rows else "-"
    layers_view.short_description = "Camadas"