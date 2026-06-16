from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
app_name = "order"

router.register(r"orders", views.OrderViewSet, basename="order")
router.register(r"create-orders", views.OrderCreateViewSet, basename="create_order")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "orders/<uuid:pk>/",
        views.OrderDetailView.as_view(),
        name="order-detail",
    ),
]
