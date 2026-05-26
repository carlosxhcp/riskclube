from django.db import models
from products.models import Product


class VipBottleModel(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="vip_models")
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="vip/models/")
    description = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=100, default="bi bi-star")
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name