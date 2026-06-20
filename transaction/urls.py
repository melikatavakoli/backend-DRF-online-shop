from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

app_name = "transaction"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "update-status-<uuid:id>/",
        views.AdminTransactionStatusUpdateAPIView.as_view(),
        name="update_status",
    ),
    path(
        "admin-list/",
        views.TransactionAdminList.as_view(),
        name="get_transaction",
    ),
    path(
        "admin-detail/<uuid:id>/",
        views.AdminTransactionDetailView.as_view(),
        name="get_transaction",
    ),
    path(
        "create/",
        views.CreatePendingTransaction.as_view(),
        name="create_transaction",
    ),
    path(
        "verify/",
        views.VerifyTransaction.as_view(),
        name="verify_transaction",
    ),
    path(
        "user-list/",
        views.UserTransactionListView.as_view(),
        name="user_transaction",
    ),
    path("request-payment/", views.RequestPayment.as_view()),
    path("callback/", views.PaymentCallback.as_view()),
]
