from django.db import models
import uuid


class VipBottleModel(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="vip_bottle_models"
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to="vip/bottle_models/"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CategoriaGravacao(models.Model):
    nome = models.CharField(max_length=80)
    icone = models.ImageField(
        upload_to="vip/categorias/"
    )
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Categoria de gravação"
        verbose_name_plural = "Categorias de gravação"

    def __str__(self):
        return self.nome


class Gravacao(models.Model):
    categoria = models.ForeignKey(
        CategoriaGravacao,
        on_delete=models.CASCADE,
        related_name="gravacoes"
    )
    nome = models.CharField(
        max_length=80,
        blank=True
    )
    imagem = models.ImageField(
        upload_to="vip/gravacoes/"
    )
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Gravação"
        verbose_name_plural = "Gravações"

    def __str__(self):
        return self.nome or f"Gravação #{self.id}"


class BottleCustomization(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)  # ajuste o app
    name = models.CharField(max_length=30, blank=True)
    font = models.CharField(max_length=50, blank=True)
    layers = models.JSONField(default=list)
    texture = models.ImageField(upload_to="customizations/texture/")
    preview = models.ImageField(upload_to="customizations/preview/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Personalização {str(self.id)[:8]} - {self.product}"