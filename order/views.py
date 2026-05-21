from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from common.paginations import CustomLimitOffsetPagination
from .filters import OrderFilter
from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderSerializer,
)
from .types import OrderStatus


class OrderCreateViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ["status", "is_successful"]
    ordering_fields = ["created_at", "updated_at"]

    queryset = (
        Order.objects.all()
        .select_related("user", "done_by")
        .prefetch_related(
            Prefetch(
                "items", queryset=OrderItem.objects.select_related("product")
            )
        )
    )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        order = self.get_object()
        user = request.user
        if order.status == OrderStatus.CANCELED:
            return Response(
                {"detail": "Order is already canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]
            or order.is_successful
        ):
            return Response(
                {"detail": "Completed orders cannot be canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if order.user != user and not user.is_staff:
            return Response(
                {
                    "detail": "You do not have permission to cancel this order."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        order.status = OrderStatus.CANCELED
        order.is_successful = False
        order.done_by = user if user.is_staff else None
        order.save()
        return Response(
            {"detail": "Order successfully canceled."},
            status=status.HTTP_200_OK,
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
