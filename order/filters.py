import django_filters
from django_filters.rest_framework import FilterSet

from common.filters import BaseFilter
from .models import Order


class OrderFilter(BaseFilter, FilterSet):
    status = django_filters.CharFilter(method="filter_status")
    is_successful = django_filters.BooleanFilter(
        method="filter_is_successful"
    )
    order_no = django_filters.CharFilter(method="filter_order_no")
    course_grade = django_filters.CharFilter(method="filter_course_grade")
    course_field = django_filters.CharFilter(method="filter_course_field")
    course = django_filters.CharFilter(method="filter_course")
    product = django_filters.CharFilter(method="filter_product")

    class Meta:
        model = Order
        fields = [
            "status",
            "is_successful",
            "order_no",
            "course_grade",
            "course_field",
            "course",
            "product",
        ]

    def filter_status(self, queryset, name, value):
        return self.filter_csv(queryset, "status", value)

    def filter_is_successful(self, queryset, name, value):
        return queryset.filter(is_successful=value)

    def filter_order_no(self, queryset, name, value):
        return self.filter_text(queryset, "order_no", value)

    def filter_course_grade(self, queryset, name, value):
        return self.filter_comma_separated(
            queryset, "items__course__grade", value
        )

    def filter_course_field(self, queryset, name, value):
        return self.filter_comma_separated(
            queryset, "items__course__field", value
        )

    def filter_course(self, queryset, name, value):
        return queryset.filter(items__course__id=value)

    def filter_product(self, queryset, name, value):
        return queryset.filter(items__product__id=value)
