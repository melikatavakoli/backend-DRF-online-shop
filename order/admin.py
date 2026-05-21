from django.contrib import admin

from common.admin import BaseAdmin, SoftDeleteListFilter
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total_price", "total_discount")
    fields = ("product", "quantity", "total_price", "total_discount")
    can_delete = True


@admin.register(Order)
class OrderAdmin(BaseAdmin):
    list_display = (
        "order_no",
        "user",
        "status",
        "is_successful",
        "total_price",
        "total_discount",
        "payable_amount",
        "total_quantity",
        "_created_at",
        "_updated_at",
    )
    list_filter = (
        SoftDeleteListFilter,
        "status",
        "is_successful",
    )
    list_editable = ("is_successful",)
    search_fields = ("order_no",)
    readonly_fields = (
        "order_no",
        "total_price",
        "total_discount",
        "payable_amount",
        "total_quantity",
        "product_types",
        "_created_at",
        "_updated_at",
        "_deleted_at",
    )
    inlines = [OrderItemInline]
    ordering = ("-_created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(BaseAdmin):
    list_display = (
        "order",
        "product",
        "quantity",
        "total_price",
        "total_discount",
    )
    list_filter = (
        SoftDeleteListFilter,
        "product",
    )
    search_fields = ("order__order_no", "product__title")
    ordering = ("-_created_at",)
    readonly_fields = (
        "_created_at",
        "_updated_at",
        "_deleted_at",
        "total_price",
        "total_discount",
    )
