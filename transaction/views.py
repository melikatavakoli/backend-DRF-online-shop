import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters, generics
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import filters as drf_filters
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.shortcuts import redirect

from common.paginations import CustomLimitOffsetPagination
from invoice.models import Invoice
from transaction.models import Transaction, PaymentReceipt
from transaction.serializers import (
    TransactionSerializer,
    PaymentReceiptSerializer,
    TransactionAdminListSerializer, 
    TransactionUserListSerializer
    )   
from transaction.choices import TransactionStatus

User = get_user_model()


class PaymentReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentReceiptSerializer
    permission_classes = [IsAuthenticated]
    queryset = PaymentReceipt.objects.all()


class AdminTransactionStatusUpdateAPIView(generics.UpdateAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        transaction = self.get_object()
        status_val = request.data.get("status", transaction.status)
        transaction.status = status_val
        transaction.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(transaction)
        return Response({
            "message": f"Transaction status updated successfully to '{transaction.status}'",
            "transaction": serializer.data
        }, status=status.HTTP_200_OK)
    

class TransactionAdminList(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionAdminListSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "description",
        'user__first_name',
        'user__last_name',
        'full_name_annotated'
    ]
    ordering_fields = [
        'amount',
        'status',
        'created_at',
        'description',
        'user__first_name',
        'user__last_name',
        'full_name_annotated'
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Transaction.objects
            .select_related("user")
            .annotate(
                full_name_annotated=Concat(
                    F("user__first_name"),
                    Value(" "),
                    F("user__last_name"),
                    output_field=CharField(),
                )
            )
        )

        if getattr(user, "role", None) == "admin":
            return queryset
        return queryset.filter(user=user)


class AdminTransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id" 

    def get_queryset(self):
        return Transaction.objects.all().order_by("-created_at")


class UserTransactionListView(generics.ListAPIView):
    serializer_class = TransactionUserListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["description"]
    ordering_fields = ["created_at", 'description', 'amount', 'status']
    ordering = ["-created_at"]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by("-created_at")
    
class CreatePendingTransaction(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        amount = request.data.get('amount')
        invoice_id = request.data.get('invoice_id')

        if not amount or int(amount) < 10000:
            return Response(
                {'message': 'Minimum transaction amount is 10,000 Tomans!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Transaction.objects.filter(user=request.user, status=TransactionStatus.pending).exists():
            return Response(
                {'message': 'Error: You have an unpaid transaction!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now_date = timezone.now()
        today_transactions = Transaction.objects.filter(
            user=request.user,
            created_at__year=now_date.year,
            created_at__month=now_date.month,
            created_at__day=now_date.day
        )
        total_today_transactions = sum(t.amount for t in today_transactions if t.amount)

        if total_today_transactions >= 500000 and not request.user.verified_national_id:
            return Response({'message': 'To charge more than 500,000 Tomans, you must verify your national ID.'}, status=status.HTTP_400_BAD_REQUEST)
        elif total_today_transactions + int(amount) > 500000 and not request.user.verified_national_id:
            return Response({'message': 'To charge more than 500,000 Tomans, you must verify your national ID.'}, status=status.HTTP_400_BAD_REQUEST)
        elif total_today_transactions >= 1500000:
            return Response({'message': 'To charge more than 1,500,000 Tomans, you must verify your account.'}, status=status.HTTP_400_BAD_REQUEST)
        elif total_today_transactions + int(amount) > 1500000:
            return Response({'message': 'To charge more than 1,500,000 Tomans, you must verify your account.'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = None
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id)
            except Invoice.DoesNotExist:
                return Response({'message': 'Invoice not found!'}, status=status.HTTP_404_NOT_FOUND)

        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            status=TransactionStatus.pending,
            invoice=invoice
        )

        return Response({'transaction_id': transaction.id}, status=status.HTTP_201_CREATED)


class VerifyTransaction(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        transaction_id = request.data.get('transaction_id')
        track_id = request.data.get('trackId')

        transaction = Transaction.objects.filter(id=transaction_id).first()
        to_toman_rate = 10

        if not transaction:
            return Response({'message': 'Transaction not found!'}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'merchant': settings.ZIBAL_MERCHANT,
            'trackId': track_id
        }
        url = 'https://gateway.zibal.ir/v1/verify' 

        try:
            response = requests.post(url, json=data, timeout=50)
        except Exception:
            return Response({'message': 'Error connecting to server!'}, status=status.HTTP_400_BAD_REQUEST)

        response_json = response.json()

        if response_json.get('status') == 'success': 
            if response_json.get('amount', 0) == int(float(transaction.amount) * to_toman_rate):
                
                transaction.status = TransactionStatus.SUCCESS
                transaction.track_id = track_id
                transaction.ref_number = response_json.get('ref_id', '')
                transaction.save(update_fields=[
                    "status", 
                    "track_id", 
                    "ref_number", 
                    "updated_at"
                    ])
                
                cart = transaction.cart
                if cart:
                    cart.cart_items.all().delete()
            
                return Response({
                    'message': response_json.get('message', ''),
                    'transaction_id': transaction_id
                }, status=status.HTTP_200_OK)
                
            else:
                return Response({'message': 'Invalid values!'}, status=status.HTTP_400_BAD_REQUEST)
            
        elif response_json.get('result') == 202:
            transaction.status = TransactionStatus.REJECTED
            transaction.track_id = track_id
            transaction.save(update_fields=[
                "status", 
                "track_id", 
                "updated_at"
                ])
            
            return Response({
                'message': response_json.get('message', ''),
                'result': response_json.get('result', ''),
                'transaction_id': transaction_id
            }, status=status.HTTP_200_OK)
            
        else:
            return Response(response_json, status=status.HTTP_200_OK)


class RequestPayment(APIView):
    permission_classes = [IsAuthenticated]
    
def post(self, request):
    transaction_id = request.data.get('transaction_id')
    
    try:
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    except Transaction.DoesNotExist:
        return Response({'message': 'Transaction not found!'}, status=status.HTTP_404_NOT_FOUND)
    
    data = {
        'merchant': settings.ZIBAL_MERCHANT,
        'amount': int(transaction.amount),
        'callbackUrl': 'https://yourdomain.com/api/v1/transaction/callback/',
        'description': f'Payment for order number {transaction.id}'
    }
    
    try:
        response = requests.post('https://gateway.zibal.ir/v1/request', json=data, timeout=30)
        result = response.json()
        
        if result.get('result') == 100:
            track_id = result.get('trackId')
            transaction.track_id = track_id
            transaction.save(update_fields=['track_id', 'updated_at'])

            payment_url = f'https://gateway.zibal.ir/start/{track_id}'
            
            return Response({
                'payment_url': payment_url,
                'track_id': track_id,
                'transaction_id': transaction.id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Error connecting to payment gateway',
                'result': result
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    

class PaymentCallback(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        track_id = request.query_params.get('trackId')
        success = request.query_params.get('success')
        if not track_id:
            return Response({'message': 'trackId parameter is missing'}, status=400)
        return redirect(f'https://yourdomain.com/payment-result?trackId={track_id}&success={success}')