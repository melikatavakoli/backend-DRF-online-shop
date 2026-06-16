from common.serializers import GenericModelSerializer
from rest_framework import serializers

from course.serializers import CourseDetailSerializer, CourseListSerializer
from product.serializers import ProductDetailSerializer, ProductListSerializer
from users.serializers import StudentDetailSerializer
from .models import Order, OrderItem


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("product", "course", "quantity")

    def validate(self, attrs):
        product = attrs.get("product")
        course = attrs.get("course")
        if bool(product) == bool(course):
            raise serializers.ValidationError(
                {"non_field_errors": "Provide either product or course, not both."}
            )
        return attrs


class OrderItemSerializer(GenericModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.FloatField(read_only=True)
    total_discount = serializers.FloatField(read_only=True)
    course = CourseListSerializer(read_only=True)
    category = serializers.CharField(
        source="product.category.title",
        read_only=True,
        default=None,
    )

    class Meta:
        model = OrderItem
        fields = GenericModelSerializer.Meta.fields + (
            "product",
            "category",
            "quantity",
            "total_price",
            "total_discount",
            "course",
        )


class OrderCreateSerializer(GenericModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("user", "status", "items")

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user
        order = Order.objects.create(user=user)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class OrderSerializer(GenericModelSerializer):
    done_by = StudentDetailSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.FloatField(read_only=True)
    total_discount = serializers.FloatField(read_only=True)
    payable_amount = serializers.FloatField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    product_types = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Order
        fields = GenericModelSerializer.Meta.fields + (
            "order_no",
            "done_by",
            "status",
            "is_successful",
            "items",
            "total_price",
            "total_discount",
            "payable_amount",
            "total_quantity",
            "product_types",
        )


class OrderItemDetailSerializer(GenericModelSerializer):
    product = ProductDetailSerializer(read_only=True)
    course = CourseDetailSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = GenericModelSerializer.Meta.fields + (
            "product",
            "course",
            "quantity",
        )


class OrderDetailSerializer(GenericModelSerializer):
    user = StudentDetailSerializer(read_only=True)
    done_by = StudentDetailSerializer(read_only=True)
    items = OrderItemDetailSerializer(many=True, read_only=True)
    total_price = serializers.FloatField(read_only=True)
    total_discount = serializers.FloatField(read_only=True)
    payable_amount = serializers.FloatField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    product_types = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Order
        fields = GenericModelSerializer.Meta.fields + (
            "order_no",
            "user",
            "done_by",
            "status",
            "is_successful",
            "items",
            "total_price",
            "total_discount",
            "payable_amount",
            "total_quantity",
            "product_types",
        )
