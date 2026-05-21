from django.contrib import admin

from common.admin import BaseAdmin, SoftDeleteListFilter
from users.models import (
    Consultant,
    Speciality,
    Student,
    TopStudent,
)
from users.resources import (
    ConsultantResource,
    StudentResource,
    TopStudentResource,
)


@admin.register(Consultant)
class ConsultantAdmin(BaseAdmin):
    resource_class = ConsultantResource
    list_display = (
        "user",
        "is_present",
        "education",
        "major",
        "_deleted_at",
        "_is_deleted",
    )
    list_filter = (SoftDeleteListFilter, "is_present", "education")
    search_fields = ("user__first_name", "user__last_name", "user__mobile")
    ordering = ("_created_at",)
    readonly_fields = ("_deleted_at",)


@admin.register(Student)
class StudentAdmin(BaseAdmin):
    resource_class = StudentResource
    list_display = ("user", "grade", "field", "_deleted_at", "_is_deleted")
    list_filter = (SoftDeleteListFilter, "grade", "field")
    search_fields = ("user__first_name", "user__last_name", "user__mobile")
    ordering = ("-_created_at",)
    readonly_fields = ("_deleted_at",)


@admin.register(TopStudent)
class TopStudentAdmin(BaseAdmin):
    resource_class = TopStudentResource
    list_display = (
        "full_name",
        "field",
        "rank",
        "branch",
        "_created_at",
        "_updated_at",
        "_deleted_at",
        "_is_deleted",
    )
    list_filter = (SoftDeleteListFilter, "field", "branch")
    search_fields = (
        "first_name",
        "last_name",
        "student__user__first_name",
        "student__user__last_name",
    )
    ordering = ("-_created_at",)
    readonly_fields = ("_deleted_at",)


@admin.register(Speciality)
class SpecialityAdmin(BaseAdmin):
    list_display = (
        "title",
        "_created_at",
        "_updated_at",
        "_deleted_at",
        "_is_deleted",
    )
    list_filter = (SoftDeleteListFilter,)
    search_fields = ("title",)
    ordering = ("-_created_at",)
    readonly_fields = ("_deleted_at",)
