from rest_framework import serializers

from course.models import Course
from course.serializers import  CourseListSerializer
from product.models import Product
from product.serializers import  ProductListSerializer
from .models import Cart, CartItem


class CartItemsSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    course = CourseListSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "course",
            "quantity",
            "base_price",
            "final_price",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.total_price


class WriteCartItemsSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False, allow_null=True
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = CartItem
        fields = ["product", "course", "quantity"]

    def validate(self, attrs):
        product = attrs.get("product")
        course = attrs.get("course")

        if not product and not course:
            raise serializers.ValidationError(
                "Either product or course must be provided."
            )
        if product and course:
            raise serializers.ValidationError("You cannot add both product and course.")
        return attrs


class UpdateCartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ["quantity"]


class RemoveCartItemSerializer(serializers.Serializer):
    item = serializers.IntegerField()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemsSerializer(many=True, source="cart_items", read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.SerializerMethodField()
    total_base_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "status",
            "total_quantity",
            "total_base_price",
            "total_price",
            "items",
        ]

    def get_total_price(self, obj):
        return obj.total_price

    def get_total_base_price(self, obj):
        return obj.total_base_price
