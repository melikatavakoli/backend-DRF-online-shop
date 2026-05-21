import django_filters
from django_filters.rest_framework import FilterSet

from common.filters import BaseFilter

from .models import Product


class ProductFilter(BaseFilter, FilterSet):
    grade = django_filters.CharFilter(method="filter_grade")
    field = django_filters.CharFilter(method="filter_field")
    is_available = django_filters.BooleanFilter(method="filter_is_available")

    class Meta:
        model = Product
        fields = [
            "category",
            "type",
            "grade",
            "field",
            "is_available",
            "has_offer",
        ]

    def filter_grade(self, queryset, name, value):
        return self.filter_csv(queryset, "grade__id", value)

    def filter_field(self, queryset, name, value):
        return self.filter_csv(queryset, "field__id", value)

    def filter_is_available(self, queryset, name, value):
        if value:
            return queryset.filter(available_quantity__gt=0)
        else:
            return queryset.filter(available_quantity__lte=0)
