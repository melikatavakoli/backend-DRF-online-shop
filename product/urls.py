from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "product"
router = routers.DefaultRouter()

router.register(r"product", views.ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
