from django.db import models
from django.conf import settings
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("percent", "Porcentagem"),
        ("fixed", "Valor fixo"),
    )

    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default="fixed"
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Deixe vazio para uso ilimitado geral."
    )

    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"

    def __str__(self):
        return self.code

    def is_valid_now(self):
        now = timezone.now()

        if not self.active:
            return False

        if self.valid_from and now < self.valid_from:
            return False

        if self.valid_until and now > self.valid_until:
            return False

        if self.max_uses is not None:
            if self.usages.count() >= self.max_uses:
                return False

        return True

    def calculate_discount(self, subtotal):
        if self.discount_type == "percent":
            return subtotal * (self.discount_value / 100)

        return min(self.discount_value, subtotal)


class CouponUsage(models.Model):
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    email = models.EmailField(blank=True)

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Uso de cupom"
        verbose_name_plural = "Usos de cupons"

        constraints = [
            models.UniqueConstraint(
                fields=["coupon", "user"],
                name="unique_coupon_per_user"
            ),
            models.UniqueConstraint(
                fields=["coupon", "email"],
                name="unique_coupon_per_email"
            ),
        ]

    def __str__(self):
        return f"{self.coupon.code} - {self.user or self.email}"