from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_id",
        "name",
        "size",
        "color",
        "custom_name",
        "quantity",
        "price",
        "subtotal",
        "image",
    )

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "email",
        "subtotal",
        "shipping_price",
        "discount",
        "total",
        "created_at",
        "paid_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("id", "email", "infinitepay_reference")
    readonly_fields = ("created_at", "paid_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "name",
        "size",
        "color",
        "custom_name",
        "quantity",
        "price",
        "subtotal",
    )

    search_fields = ("name", "custom_name", "order__email")