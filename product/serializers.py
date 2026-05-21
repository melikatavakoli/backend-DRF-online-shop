from django.db import transaction
from rest_framework import serializers

from common.serializers import GenericModelSerializer
from course.models import Field, Grade
from course.serializers import (
    CategorySerializer,
    FieldSerializer,
    GradeSerializer,
)
from .models import Product


class ProductBaseSerializer(GenericModelSerializer):
    class Meta:
        model = Product
        fields = GenericModelSerializer.Meta.fields + (
            "title",
            "description",
            "final_price",
            "base_price",
            "category",
            "education_level",
            "available_quantity",
            "image",
            "type",
            "has_offer",
            "offer",
            "slug",
        )


class ProductWriteSerializer(ProductBaseSerializer):
    grade = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.all(), many=True, required=False
    )
    field = serializers.PrimaryKeyRelatedField(
        queryset=Field.objects.all(), many=True, required=False
    )

    class Meta(ProductBaseSerializer.Meta):
        fields = ProductBaseSerializer.Meta.fields + (
            "grade",
            "field",
        )
        read_only_fields = ("final_price", "slug")

    @transaction.atomic
    def create(self, validated_data):
        grades = validated_data.pop("grade", [])
        fields = validated_data.pop("field", [])
        product = Product.objects.create(**validated_data)
        if grades:
            product.grade.set(grades)
        if fields:
            product.field.set(fields)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        grades = validated_data.pop("grade", None)
        fields = validated_data.pop("field", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if grades is not None:
            instance.grade.set(grades)
        if fields is not None:
            instance.field.set(fields)
        return instance


class ProductListSerializer(ProductBaseSerializer):
    grade = GradeSerializer(read_only=True, many=True)
    field = FieldSerializer(read_only=True, many=True)

    class Meta(ProductBaseSerializer.Meta):
        fields = ProductBaseSerializer.Meta.fields + (
            "grade",
            "field",
        )


class ProductDetailSerializer(ProductBaseSerializer):
    grade = GradeSerializer(read_only=True, many=True)
    field = FieldSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    final_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta(ProductBaseSerializer.Meta):
        fields = ProductBaseSerializer.Meta.fields + (
            "grade",
            "field",
            "is_available",
        )
