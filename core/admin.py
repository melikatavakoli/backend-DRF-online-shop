from django.contrib import admin
from common.admin import BaseAdmin, SoftDeleteListFilter
from .models import BaseUser


@admin.register(BaseUser)
class BaseUserAdmin(BaseAdmin):
    list_display = (
        "id",
        "full_name",
        "mobile",
        "email",
        "role",
        "is_verified",
        "is_email_verified",
        "city",
        "country",
        "_created_at_display",
    )

    list_filter = (
        SoftDeleteListFilter,
        "role",
        "is_verified",
        "is_email_verified",
        "country",
        "state",
        "city",
    )

    search_fields = (
        "mobile",
        "email",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "password__updated_at",
        "_is_deleted",
        "_deleted_at",
    )

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "mobile",
                "email",
                "first_name",
                "last_name",
                "birth_date",
                "role",
                "description",
            )
        }),
        ("Location", {
            "fields": (
                "country",
                "state",
                "city",
            )
        }),
        ("Verification", {
            "fields": (
                "is_verified",
                "is_email_verified",
            )
        }),
        ("Security", {
            "fields": (
                "password",
                "password__updated_at",
                "last_login",
                "last_login_ip",
            )
        }),
    )

    def delete_queryset(self, request, queryset):
        queryset.delete()

    def delete_model(self, request, obj):
        obj.delete()