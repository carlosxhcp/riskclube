from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    category = models.CharField(
    max_length=30,
    choices=[
        ("termicas", "Térmicas"),
        ("squeeze", "Squeeze"),
        ("personalizadas", "Personalizadas"),
    ],
    default="termicas",
)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(upload_to="products/")
    image_hover = models.ImageField(upload_to="products/", blank=True, null=True)

    description = models.TextField(blank=True)

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

    is_vip = models.BooleanField(default=False, verbose_name="Produto VIP")

    class Meta:
        ordering = ["-created"]

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
    image = models.ImageField(upload_to="products/variants/")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} - {self.color_name}"


class VariantImage(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="products/variant_gallery/")

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

    def __str__(self):
        return f"{self.variant.color_name} - {self.name}"

class EngravingMockup(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="engraving_mockups"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="engraving_mockups",
        blank=True,
        null=True
    )

    name = models.CharField(max_length=100)
    
    thumbnail = models.ImageField(
    upload_to="engraving_mockups/thumbs/"
)

    main_image = models.ImageField(
        upload_to="engraving_mockups/main/"
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EngravingMockupImage(models.Model):
    mockup = models.ForeignKey(
        EngravingMockup,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="engraving_mockups/gallery/")
    alt = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Imagem extra do mockup"
        verbose_name_plural = "Imagens extras do mockup"

    def __str__(self):
        return f"Imagem de {self.mockup.name}"