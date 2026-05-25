from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
app_name = "invoice"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "admin/",
        views.AdminInvoiceAPIView.as_view(),
        name="admin_list_invoice",
    ),
    path(
        "cancel-<uuid:invoice_id>/",
        views.CancelInvoiceAPIView.as_view(),
        name="admin_cancel_invoice",
    ),
    path("create/", views.InvoiceAPIView.as_view(), name="invoice-create"),
    path(
        "<uuid:invoice_id>/",
        views.RetrieveInvoiceAPIView.as_view(),
        name="get_invoice_by_id",
    ),
    path(
        "user/",
        views.UserInvoiceAPIView.as_view(),
        name="user_list_invoice",
    ),
]
