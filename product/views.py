from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from common.paginations import CustomLimitOffsetPagination
from product.filters import ProductFilter
from .models import Product
from .serializers import (
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = ["_created_at", "_updated_at"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductWriteSerializer
        elif self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related(
            "grade", "field"
        )
