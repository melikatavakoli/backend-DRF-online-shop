import django_filters


class BaseFilter(django_filters.FilterSet):
    """Base filter with support for comma-separated and text search filters."""

    def filter_csv(self, queryset, field_name, value):
        """Filter by comma-separated values. Example: ?ids=1,2,3"""
        values = [v.strip() for v in value.split(",") if v.strip()]
        return queryset.filter(**{f"{field_name}__in": values}).distinct() if values else queryset

    def filter_text(self, queryset, field_name, value):
        """Filter by text search. Example: ?name=john"""
        return queryset.filter(**{f"{field_name}__icontains": value}).distinct()
