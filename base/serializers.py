from django.contrib.auth import get_user_model
from django.db import models
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        fields = ("id", "created_by", "updated_by", "created_at", "updated_at", "can_delete")
        read_only_fields = fields

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            for name, field in self.fields.items():
                if name in data and data[name] == "" and isinstance(field, serializers.CharField):
                    data[name] = None
        return super().to_internal_value(data)

    @extend_schema_field(serializers.CharField)
    def get_created_at(self, obj):
        return obj.created_at_display

    @extend_schema_field(serializers.CharField)
    def get_updated_at(self, obj):
        return obj.updated_at_display

    @extend_schema_field(serializers.BooleanField)
    def get_can_delete(self, obj):
        return getattr(obj, "can_delete", False)
