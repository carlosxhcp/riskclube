
from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import (
    VipBottleModel,
    CategoriaGravacao,
    Gravacao,
    BottleCustomization,
)


# =========================================================
# MODELOS DE GARRAFAS VIP
# =========================================================

@admin.register(VipBottleModel)
class VipBottleModelAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "product", "is_active")
    list_display_links = ("name",)
    list_filter = ("is_active",)
    search_fields = ("name", "product__name")
    list_per_page = 25

    @admin.display(description="Imagem")
    def preview(self, obj):
        if not obj.image:
            return "Sem imagem"

        return format_html(
            '<img src="{}" style="width:65px;height:75px;'
            'object-fit:contain;background:#f3f3f3;'
            'border-radius:6px;padding:4px;">',
            obj.image.url,
        )


# =========================================================
# GRAVAÇÕES DENTRO DA CATEGORIA
# =========================================================

class GravacaoInline(admin.TabularInline):
    model = Gravacao
    extra = 0
    show_change_link = True

    fields = ("preview", "nome", "imagem", "ativo", "ordem")
    readonly_fields = ("preview",)

    @admin.display(description="Prévia")
    def preview(self, obj):
        if not obj or not obj.imagem:
            return "Sem imagem"

        return format_html(
            '<img src="{}" style="width:55px;height:55px;'
            'object-fit:contain;background:#f3f3f3;'
            'border-radius:6px;padding:3px;">',
            obj.imagem.url,
        )


# =========================================================
# CATEGORIAS DE GRAVAÇÃO
# =========================================================

@admin.register(CategoriaGravacao)
class CategoriaGravacaoAdmin(admin.ModelAdmin):
    list_display = ("preview_icone", "nome", "ativo", "ordem")
    list_display_links = ("nome",)
    list_editable = ("ativo", "ordem")
    list_filter = ("ativo",)
    search_fields = ("nome",)
    ordering = ("ordem", "nome")
    inlines = (GravacaoInline,)
    list_per_page = 25

    @admin.display(description="Ícone")
    def preview_icone(self, obj):
        if not obj.icone:
            return "Sem ícone"

        return format_html(
            '<img src="{}" style="width:48px;height:48px;'
            'object-fit:contain;background:#f3f3f3;'
            'border-radius:6px;padding:3px;">',
            obj.icone.url,
        )


# =========================================================
# GRAVAÇÕES
# =========================================================

@admin.register(Gravacao)
class GravacaoAdmin(admin.ModelAdmin):
    list_display = (
        "preview",
        "nome",
        "categoria",
        "ativo",
        "ordem",
    )
    list_display_links = ("nome",)
    list_filter = ("categoria", "ativo")
    list_editable = ("ativo", "ordem")
    search_fields = ("nome", "categoria__nome")
    ordering = ("categoria__ordem", "ordem", "nome")
    list_per_page = 30

    @admin.display(description="Imagem")
    def preview(self, obj):
        if not obj.imagem:
            return "Sem imagem"

        return format_html(
            '<img src="{}" style="width:58px;height:58px;'
            'object-fit:contain;background:#f3f3f3;'
            'border-radius:6px;padding:3px;">',
            obj.imagem.url,
        )


# =========================================================
# PERSONALIZAÇÕES DE GARRAFAS
# =========================================================

@admin.register(BottleCustomization)
class BottleCustomizationAdmin(admin.ModelAdmin):
    change_form_template = (
        "admin/customization/bottlecustomization/change_form.html"
    )

    list_display = (
        "preview_list",
        "product",
        "name",
        "font",
        "created_at",
        "texture_status",
    )
    list_display_links = ("preview_list", "product")
    list_filter = ("product", "created_at")
    search_fields = ("name", "font", "product__name", "id")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    list_select_related = ("product",)

    fields = (
        "product",
        "name",
        "font",
        "preview_view",
        "texture_view",
        "layers_view",
        "created_at",
    )

    readonly_fields = (
        "preview_view",
        "texture_view",
        "layers_view",
        "created_at",
    )

    fieldsets = (
        (
            "Identificação",
            {
                "fields": ("product", "name", "font"),
            },
        ),
        (
            "Arquivos da personalização",
            {
                "fields": ("preview_view", "texture_view"),
                "description": (
                    "Confira a imagem final e a textura PNG "
                    "salva nesta personalização."
                ),
            },
        ),
        (
            "Camadas da gravação",
            {
                "fields": ("layers_view",),
            },
        ),
        (
            "Registro",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Prévia")
    def preview_list(self, obj):
        if not obj.preview:
            return format_html(
                '<span style="color:#888;">Sem prévia</span>'
            )

        return format_html(
            '<img src="{}" style="width:65px;height:75px;'
            'object-fit:contain;background:#f3f3f3;'
            'border-radius:6px;padding:3px;">',
            obj.preview.url,
        )

    @admin.display(description="Imagem final")
    def preview_view(self, obj):
        if not obj or not obj.preview:
            return format_html(
                '<span style="color:#888;">'
                'Nenhuma imagem de prévia foi salva.'
                '</span>'
            )

        return format_html(
            '<div style="display:inline-block;padding:12px;'
            'background:#f3f3f3;border:1px solid #ddd;'
            'border-radius:8px;">'
            '<a href="{}" target="_blank" rel="noopener">'
            '<img src="{}" alt="Prévia da garrafa" '
            'style="display:block;max-width:360px;'
            'max-height:420px;object-fit:contain;">'
            '</a></div>'
            '<p><a href="{}" target="_blank" rel="noopener">'
            'Abrir imagem original</a></p>',
            obj.preview.url,
            obj.preview.url,
            obj.preview.url,
        )

    @admin.display(description="Textura PNG")
    def texture_view(self, obj):
        if not obj or not obj.texture:
            return format_html(
                '<span style="color:#888;">'
                'Nenhuma textura foi salva.'
                '</span>'
            )

        url = obj.texture.url

        return format_html(
            '<div style="display:inline-block;max-width:100%;">'
            '<div style="background:#242424;padding:12px;'
            'border-radius:8px;border:1px solid #555;">'
            '<img src="{}" alt="Textura PNG" '
            'style="display:block;width:100%;max-width:420px;'
            'max-height:420px;object-fit:contain;">'
            '</div>'
            '<p style="margin-top:10px;">'
            '<a href="{}" target="_blank" rel="noopener">'
            'Abrir textura original</a>'
            '</p></div>',
            url,
            url,
        )

    @admin.display(description="Camadas da gravação")
    def layers_view(self, obj):
        if not obj or not isinstance(obj.layers, list) or not obj.layers:
            return format_html(
                '<span style="color:#888;">'
                'Nenhuma camada registrada.'
                '</span>'
            )

        rows = []

        for index, layer in enumerate(obj.layers, start=1):
            if not isinstance(layer, dict):
                continue

            layer_type = layer.get("type", "")

            if layer_type == "name":
                title = f'Nome: {layer.get("text") or "(vazio)"}'
                detail = f'Fonte: {layer.get("font") or obj.font or "-"}'
            else:
                title = f'Gravação: {layer.get("name") or "Sem nome"}'
                detail = f'Tipo: {layer_type or "não informado"}'

            x = layer.get("x", 0)
            y = layer.get("y", 0)
            size = layer.get("size", 0)
            rotation = layer.get("rotation", 0)

            rows.append(
                (
                    index,
                    title,
                    detail,
                    str(x),
                    str(y),
                    str(size),
                    str(rotation),
                )
            )

        if not rows:
            return format_html(
                '<span style="color:#888;">'
                'Nenhuma camada válida encontrada.'
                '</span>'
            )

        header = format_html(
            '<thead><tr>'
            '<th style="padding:8px;text-align:left;">#</th>'
            '<th style="padding:8px;text-align:left;">Elemento</th>'
            '<th style="padding:8px;text-align:left;">Detalhes</th>'
            '<th style="padding:8px;">X</th>'
            '<th style="padding:8px;">Y</th>'
            '<th style="padding:8px;">Tamanho</th>'
            '<th style="padding:8px;">Rotação</th>'
            '</tr></thead>'
        )

        body = format_html_join(
            "",
            '<tr>'
            '<td style="padding:8px;">{}</td>'
            '<td style="padding:8px;">{}</td>'
            '<td style="padding:8px;">{}</td>'
            '<td style="padding:8px;text-align:center;">{}</td>'
            '<td style="padding:8px;text-align:center;">{}</td>'
            '<td style="padding:8px;text-align:center;">{}</td>'
            '<td style="padding:8px;text-align:center;">{}</td>'
            '</tr>',
            rows,
        )

        return format_html(
            '<div style="max-width:100%;overflow-x:auto;">'
            '<table style="border-collapse:collapse;'
            'width:100%;border:1px solid #ddd;">'
            '{}{}</table></div>',
            header,
            body,
        )

    @admin.display(description="Textura", boolean=True)
    def texture_status(self, obj):
        return bool(obj.texture)
