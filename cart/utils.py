from decimal import Decimal
from .models import Coupon, CouponUsage


def validate_coupon(code, subtotal, user=None, email=None):
    code = code.strip().upper()

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return False, "Cupom inválido.", None, Decimal("0.00")

    if not coupon.is_valid_now():
        return False, "Cupom expirado ou inativo.", None, Decimal("0.00")

    if subtotal < coupon.min_order_value:
        return False, f"Pedido mínimo de R$ {coupon.min_order_value}.", None, Decimal("0.00")

    if user and user.is_authenticated:
        already_used = CouponUsage.objects.filter(
            coupon=coupon,
            user=user
        ).exists()
    else:
        already_used = CouponUsage.objects.filter(
            coupon=coupon,
            email=email
        ).exists()

    if already_used:
        return False, "Você já usou este cupom.", None, Decimal("0.00")

    discount = coupon.calculate_discount(subtotal)

    return True, "Cupom aplicado com sucesso.", coupon, discount