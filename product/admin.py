from django.contrib import admin

from common.admin import BaseAdmin, SoftDeleteListFilter
from .models import Product


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "education_level",
        "available_quantity",
        "type",
        "is_available",
    )
    fields = (
        "title",
        "description",
        "final_price",
        "category",
        "grade",
        "field",
        "education_level",
        "available_quantity",
        "image",
        "slug",
        "type",
    )
    search_fields = ("title", "description", "category__name", "education_level")
    list_filter = (SoftDeleteListFilter, "category", "type", "grade", "field")
    filter_horizontal = (
        "grade",
        "field",
    )
    readonly_fields = ("_created_at", "_updated_at", "_deleted_at")
    ordering = ("title",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "grade",
                "field",
            )
        )

    def is_available(self, obj):
        return obj.is_available

    is_available.boolean = True
    is_available.short_description = "Available"
