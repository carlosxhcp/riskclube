from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    installments = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="products/")
    description = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
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

class CommunityImage(models.Model):
    image = models.ImageField(upload_to="community/")
    alt = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.alt or "Imagem da comunidade"