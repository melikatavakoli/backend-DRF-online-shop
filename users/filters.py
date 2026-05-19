import django_filters as filters

from users.models import Consultant


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class BooleanInFilter(filters.BaseInFilter, filters.BooleanFilter):
    pass


class ConsultantFilterSet(filters.FilterSet):
    specialities = NumberInFilter(field_name="specialities__id")
    education = NumberInFilter()
    role = CharInFilter(field_name="user__role")
    city = NumberInFilter(field_name="user__city_id")
    state = NumberInFilter(field_name="user__state_id")
    is_present = filters.BooleanFilter()
    is_verified = filters.BooleanFilter(field_name="user__is_verified")
    is_active = filters.BooleanFilter(field_name="user__is_active")

    class Meta:
        model = Consultant
        fields = (
            "specialities",
            "education",
            "is_present",
            "role",
            "city",
            "state",
            "is_verified",
            "is_active",
        )
