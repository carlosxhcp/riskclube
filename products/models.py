from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    ENGRAVING_POSITION_CHOICES = [
        ("none", "Nenhuma gravação"),
        ("front", "Frente"),
        ("back", "Costas"),
        ("front_back", "Frente e costas"),
    ]

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(
        upload_to="products/",
        verbose_name="Imagem da frente"
    )

    back_image = models.ImageField(
        upload_to="products/back/",
        blank=True,
        null=True,
        verbose_name="Imagem das costas / verso"
    )

    image_hover = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Imagem hover"
    )

    description = models.TextField(blank=True)

    engraving_position = models.CharField(
        max_length=20,
        choices=ENGRAVING_POSITION_CHOICES,
        default="front",
        verbose_name="Opções de gravação"
    )

    default_color_name = models.CharField(
        max_length=50,
        default="Preto"
    )

    default_color_hex = models.CharField(
        max_length=20,
        default="#000000"
    )

    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("products:product_detail", args=[self.slug])

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="products/gallery/")
    alt = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = "Imagem do produto"
        verbose_name_plural = "Imagens do produto"

    def __str__(self):
        return f"Imagem de {self.product.name}"

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    color_name = models.CharField(max_length=50)
    color_hex = models.CharField(max_length=20, default="#000000")

    image = models.ImageField(
        upload_to="products/variants/",
        verbose_name="Imagem da frente"
    )

    back_image = models.ImageField(
        upload_to="products/variants/back/",
        blank=True,
        null=True,
        verbose_name="Imagem das costas"
    )

    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Variação de cor"
        verbose_name_plural = "Variações de cor"

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"


class VariantImage(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="products/variant_gallery/")
    alt = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Imagem da variação"
        verbose_name_plural = "Imagens da variação"

    def __str__(self):
        return f"Imagem de {self.variant}"


class ProductSize(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        related_name="sizes",
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Tamanho"
        verbose_name_plural = "Tamanhos"

    def __str__(self):
        return f"{self.variant.color_name} - {self.name}"

class ProductDefaultSize(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="sizes",
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Tamanho padrão"
        verbose_name_plural = "Tamanhos padrão"

    def __str__(self):
        return f"{self.product.name} - {self.name}"