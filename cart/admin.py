from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "active",
        "discount_type",
        "discount_value",
        "min_order_value",
        "max_uses",
        "valid_from",
        "valid_until",
    )

    search_fields = ("code",)
    list_filter = ("active", "discount_type")


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "email", "used_at")
    search_fields = ("coupon__code", "user__email", "email")
    list_filter = ("coupon",)