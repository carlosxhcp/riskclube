from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("cancelled", "Cancelado"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    email = models.EmailField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    shipping_name = models.CharField(max_length=100, blank=True)
    shipping_company = models.CharField(max_length=100, blank=True)
    shipping_cep = models.CharField(max_length=20, blank=True)

    infinitepay_link = models.URLField(max_length=1000, blank=True)
    infinitepay_reference = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_id = models.PositiveIntegerField(null=True, blank=True)
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=100, blank=True)
    custom_name = models.CharField(max_length=100, blank=True)

    engraving_side = models.CharField(max_length=20, blank=True)
    name_direction = models.CharField(max_length=20, blank=True)
    name_font = models.CharField(max_length=100, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.URLField(blank=True)

    class Meta:
        verbose_name = "Item do pedido"
        verbose_name_plural = "Itens do pedido"

    def __str__(self):
        return self.name