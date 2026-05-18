import django_filters
from common.filters import BaseFilter
from course.models import Course


class CourseFilter(BaseFilter):
    grade = django_filters.CharFilter(method="filter_grade")
    field = django_filters.CharFilter(method="filter_field")
    category = django_filters.CharFilter(method="filter_category")
    has_video = django_filters.BooleanFilter(field_name="has_video")
    is_free = django_filters.BooleanFilter(field_name="is_free")
    subject = django_filters.CharFilter(method="filter_subject")
    teacher = django_filters.CharFilter(method="filter_teacher")

    class Meta:
        model = Course
        fields = [
            "grade",
            "field",
            "category",
            "has_video",
            "is_free",
            "subject",
            "teacher",
        ]

    def filter_grade(self, queryset, name, value):
        return self.filter_csv(queryset, "grade__id", value)

    def filter_field(self, queryset, name, value):
        return self.filter_csv(queryset, "field__id", value)

    def filter_category(self, queryset, name, value):
        return self.filter_csv(queryset, "category__id", value)

    def filter_subject(self, queryset, name, value):
        return self.filter_text(queryset, "subject__id", value)

    def filter_teacher(self, queryset, name, value):
        return self.filter_text(queryset, "teacher__id", value)
