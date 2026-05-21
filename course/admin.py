from django.contrib import admin
from common.admin import BaseAdmin, SoftDeleteListFilter
from .models import (
    Course,
    CourseCategory,
    CourseFeature,
    CourseLearning,
    Field,
    Grade,
    Session,
    SessionProgress,
    Subject,
    TagCourse,
    Teacher,
)


@admin.register(Teacher)
class TeacherAdmin(BaseAdmin):
    list_display = ("title", "full_name", "_created_at")
    search_fields = ("title", "full_name")
    list_filter = (SoftDeleteListFilter, "_created_at")
    ordering = ("-_created_at",)


@admin.register(Subject)
class SubjectAdmin(BaseAdmin):
    list_display = ("title", "_created_at")
    search_fields = ("title",)
    list_filter = (SoftDeleteListFilter, "_created_at")
    ordering = ("-_created_at",)


@admin.register(Grade)
class GradeAdmin(BaseAdmin):
    list_display = ("title", "_created_at")
    search_fields = ("title",)
    list_filter = (SoftDeleteListFilter,)
    ordering = ("-_created_at",)


@admin.register(Field)
class FieldAdmin(BaseAdmin):
    list_display = ("title", "_created_at")
    search_fields = ("title",)
    list_filter = (SoftDeleteListFilter,)
    ordering = ("-_created_at",)


@admin.register(Session)
class SessionAdmin(BaseAdmin):
    list_display = ("title", "is_free", "length", "_updated_at")
    list_filter = (SoftDeleteListFilter, "is_free")
    list_editable = ("is_free",)
    search_fields = ("title",)
    ordering = ("-_updated_at",)


@admin.register(SessionProgress)
class SessionProgressAdmin(BaseAdmin):
    list_display = (
        "user",
        "session",
        "watched_duration",
        "progress_percentage",
        "is_completed",
        "_updated_at",
    )
    list_filter = (SoftDeleteListFilter, "session")
    search_fields = (
        "user__mobile",
        "user__first_name",
        "user__last_name",
        "session__title",
    )
    readonly_fields = ("progress_percentage", "is_completed")
    list_select_related = ("user", "session")

    def progress_percentage(self, obj):
        return f"{obj.progress_percentage:.2f}%"

    def is_completed(self, obj):
        return obj.is_completed

    progress_percentage.short_description = "Progress"
    is_completed.boolean = True


@admin.register(CourseCategory)
class CourseCategoryAdmin(BaseAdmin):
    list_display = ("title", "total_sessions", "total_length", "_created_at")
    search_fields = ("title",)
    list_filter = (SoftDeleteListFilter,)
    filter_horizontal = ("session",)
    ordering = ("-_created_at",)

    def total_length(self, obj):
        return str(obj.total_length)

    total_length.short_description = "Total Length"


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = (
        "title",
        "status",
        "price",
        "discount_price",
        "is_free",
        "has_discount",
        "teacher",
        "total_length",
        "_created_at",
    )
    list_filter = (
        SoftDeleteListFilter,
        "status",
        "is_free",
        "has_discount",
        "teacher",
        "subject",
    )
    search_fields = ("title", "teacher__full_name", "subject__title")
    filter_horizontal = (
        "grade",
        "field",
        "category",
        "users",
    )
    autocomplete_fields = ("teacher", "subject", "users")
    list_select_related = ("teacher", "subject")
    ordering = ("-_created_at",)
    readonly_fields = ("total_length",)

    def total_length(self, obj):
        return str(obj.total_length)

    total_length.short_description = "Total Length"


@admin.register(CourseFeature)
class FeatureAdmin(BaseAdmin):
    list_display = ("text", "_created_at")
    search_fields = ("text",)
    list_filter = (SoftDeleteListFilter, "_created_at")
    ordering = ("-_created_at",)


@admin.register(CourseLearning)
class LearningAdmin(BaseAdmin):
    list_display = ("text", "_created_at")
    search_fields = ("text",)
    list_filter = (SoftDeleteListFilter, "_created_at")
    ordering = ("-_created_at",)


@admin.register(TagCourse)
class TagAdmin(BaseAdmin):
    list_display = ("text", "_created_at")
    search_fields = ("text",)
    list_filter = (SoftDeleteListFilter, "_created_at")
    ordering = ("-_created_at",)
